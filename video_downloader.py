from pytube import YouTube
#  >>> from pytube import YouTube
#  >>> YouTube('https://youtu.be/2lAe1cqCOXo').streams.first().download()
#  >>> yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')
#  >>> yt.streams
#   ... .filter(progressive=True, file_extension='mp4')
#   ... .order_by('resolution')
#   ... .desc()
#   ... .first()
#   ... .download()

def download_video_caption(url):
    # download a complete video caption and return it as a string
    yt = YouTube(url)
    # 获取可用的字幕
    captions = yt.captions

    # 打印可用的字幕语言
    print("可用的字幕语言:")
    for caption in captions:
        print(caption.code, caption.name)
        
        
    caption_code = 'en-US'

    # 获取指定语言的字幕
    if caption_code in captions:
        caption = captions[caption_code]
        
        # 下载字幕
        subtitle = caption.generate_srt_captions()  # 生成 SRT 格式字幕
        print(subtitle)  # 打印字幕内容
        return subtitle
    else:
        print(f"没有找到 {caption_code} 的字幕")
        return None
        
if __name__ == "__main__":
    url = 'https://www.youtube.com/watch?v=bCz4OMemCcA&t=6s&ab_channel=UmarJamil'
    result = download_video_caption(url)
    print(result)