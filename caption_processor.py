
import re

def read_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

def extract_captions(srt_content):
    # Regular expression to match the SRT format
    pattern = re.compile(r'\d+\n(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n\n', re.DOTALL)
    captions = pattern.findall(srt_content)
    return [caption[1].replace('\n', ' ').strip() for caption in captions]


# connect the lines to paragraphs
# max_lines lines are chunked together
def process_to_paragraphs(captions, max_lines=5):
    paragraphs = []
    current_paragraph = []
    
    for line in captions:
        current_paragraph.append(line)
        if len(current_paragraph) >= max_lines:
            paragraphs.append(' '.join(current_paragraph))
            current_paragraph = []
    
    # Add remaining lines as a paragraph
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))
    
    return paragraphs

def extract_paragraphs(file_path, max_lines=20):
    srt_content = read_srt(file_path)
    captions = extract_captions(srt_content)
    paragraphs = process_to_paragraphs(captions, max_lines)
    return paragraphs

if __name__ == "__main__":
    
    srt_file_path = "caption.srt"
    srt_content = read_srt(srt_file_path)
    captions = extract_captions(srt_content)
    paragraphs = process_to_paragraphs(captions, max_lines=20)

    print(len(paragraphs))
    # # Print or save the paragraphs
    for para in paragraphs:
        print(para)
    