import requests
from bs4 import BeautifulSoup

def get_youtube_video_info(url):
    # 获取页面 HTML
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功

    # 解析 HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取信息
    title = soup.title.string if soup.title else 'N/A'
    description = soup.find('meta', {'name': 'description'})
    description_content = description['content'] if description else 'N/A'
    uploader = soup.find('link', {'itemprop': 'name'})
    uploader_name = uploader['content'] if uploader else 'N/A'
    upload_date = soup.find('meta', {'itemprop': 'datePublished'})
    upload_date_content = upload_date['content'] if upload_date else 'N/A'

    return {
        "title": title,
        "description": description_content,
        "uploader": uploader_name,
        "upload_date": upload_date_content,
        "url": url
    }


if __name__ == "__main__":
    # 示例 YouTube 视频 URL
    url = "https://www.youtube.com/watch?v=bCz4OMemCcA&t=6s&ab_channel=UmarJamil"

    # 获取视频信息
    video_info = get_youtube_video_info(url)

    # 打印结果
    print(video_info)