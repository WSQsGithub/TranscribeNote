import requests
import json
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from caption_processor import extract_paragraphs
from meta_retriever import get_youtube_video_info

load_dotenv()

openai_api_key = os.getenv("CHAT_API_KEY")  
url = "https://api.chatanywhere.tech/v1/chat/completions"
headers = {
   'Authorization': f'Bearer {openai_api_key}',
   'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
   'Content-Type': 'application/json'
}


with open('topic_templates.json', 'r', encoding='utf-8') as json_file:
    topic2template = json.load(json_file)

topic_msg = f"""You are given meta data to a video, please choose the most appropriate topic from the list: {topic2template.keys()}, return a single word indicating the topic, do not return any topics outside the list"""

summary_msg = """You are given a potentially incomplete speech transcript, provide a brief summary of approximately 200 words for every paragraph you receive"""

note_msg = """You are given a speech summary, please provide a lecture note in following structure in markdown: """


def parse_gpt_response(gpt_response_json):
    """
    解析 GPT 的 JSON 回复并提取信息。

    参数:
    gpt_response_json (str): GPT 的 JSON 回复字符串。

    返回:
    dict: 包含角色、内容和使用情况的字典。
    """
    # 解析 JSON
    try:
        gpt_response = json.loads(gpt_response_json)
        
        # 提取所需信息
        message = gpt_response['choices'][0]['message']
        content = message['content']
        role = message['role']
        usage = gpt_response['usage']
        
        # 返回提取的信息
        return {
            "role": role,
            "content": content,
            "usage": usage
        }
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"An error occurred while parsing the GPT response: {e}")
        return {
            "role": None,
            "content": None,
            "usage": None
        }
    
    

def match_topic(meta):
    """
    Matches a topic based on the provided video metadata using a GPT-4 model.
    Args:
        meta (str): The metadata of the video to be used for matching the topic.
    Returns:
        str: The matched topic content extracted from the GPT-4 model response.
    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
        KeyError: If the expected content is not found in the response.
    """
    # 构造请求的提示消息

    payload = json.dumps(
        {
            "model": "gpt-4o-mini",
            "messages": [
            {
                "role": "system",
                "content": topic_msg
            },
            {
                "role": "user",
                "content": f"Video meta: {meta}"
            }
            ]
        }
    )
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        matched_topic = parse_gpt_response(response.text)
        return matched_topic["content"]
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    except KeyError as e:
        print(f"Key error: {e}")
        return None
    
def summarize_paragraph(paragraph):
    """
    Summarizes the given paragraph using an external GPT-4 model.
    Args:
        paragraph (str): The paragraph to be summarized.
    Returns:
        str: The summarized version of the paragraph.
    Raises:
        requests.exceptions.RequestException: If the request to the GPT-4 model fails.
        ValueError: If the response from the GPT-4 model cannot be parsed.
    Note:
        This function sends a POST request to a specified URL with the paragraph
        to be summarized. The response is then parsed to extract the summary.
    """
    
    payload = json.dumps(
        {
            "model": "gpt-4o-mini",
            "messages": [
            {
                "role": "system",
                "content": summary_msg
            },
            {
                "role": "user",
                "content": f"Paragraph: {paragraph}"
            }
            ]
        }
    )
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return parse_gpt_response(response.text)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
    

def generate_note(topic, summaries):
    """
    Generates a note based on a given topic and a list of summaries.
    Args:
        topic (str): The topic for which the note is to be generated.
        summaries (list of str): A list of summary strings to be concatenated and used in the note generation.
    Returns:
        str: The generated note as a string.
    Raises:
        Exception: If the request to the OpenAI API fails or if the response cannot be parsed.
    """
    
    # concate the summaries into one str
    summaries_concat = ""
    
    for s in summaries:
        summaries_concat += f"\n{s}"
    
    system_prompt = note_msg + topic2template[topic]
    
    
    # summarize text from a paragraph with openai
    payload = json.dumps(
        {
            "model": "gpt-4o-mini",
            "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"Summary: {summaries_concat}"
            }
            ]
        }
    )
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return parse_gpt_response(response.text)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
    
def pipeline(topic, paragraphs):
    
    
    with ThreadPoolExecutor() as executor:
        summaries = list(executor.map(summarize_paragraph, paragraphs))
    
    note = generate_note(topic, summaries)
    
    return note


def write_to_md_file(meta, content, filename='output.md'):
    """
    Writes metadata and content to a Markdown file.
    Args:
        meta (dict): A dictionary containing metadata to be written in YAML format.
        content (str): The main content to be written to the Markdown file.
        filename (str, optional): The name of the output Markdown file. Defaults to 'output.md'.
    Returns:
        None
    """

    with open(filename, 'w', encoding='utf-8') as md_file:
        yaml_meta = "---\n"
        for key, value in meta.items():
            yaml_meta += f"{key}: {value}\n"
        yaml_meta += "---\n\n"  # 添加分隔线

        # 写入 YAML 元信息
        md_file.write(yaml_meta)
        
        # 写入内容
        md_file.write(f"{content}\n")
        
def retrieve_meta_and_match_topic(video_url):
    """Retrieve video metadata and match the topic."""
    meta = get_youtube_video_info(video_url)  # Retrieve video info
    topic = match_topic(meta)  # Match the topic
    meta["tag"] = topic  # Add the topic tag to meta
    return meta

if __name__ == "__main__":
    
    video_url = "https://www.youtube.com/watch?v=bCz4OMemCcA&t=6s&ab_channel=UmarJamil"
    caption_path = "caption.srt"
    
    with ThreadPoolExecutor() as executor:
        # Submit tasks to the executor
        future_meta = executor.submit(retrieve_meta_and_match_topic, video_url)
        future_paragraphs = executor.submit(extract_paragraphs, caption_path, 50) # this is supposed to run longer if only video url is provided

        # Retrieve results
        meta = future_meta.result()
        paragraphs = future_paragraphs.result()
    
    # paragraphs = extract_paragraphs("caption.srt", max_lines=50)
    
    note = pipeline(meta["tag"], paragraphs)
    
    write_to_md_file(meta, note["content"])
    