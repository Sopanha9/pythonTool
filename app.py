import yt_dlp 

import os 

video_url = "https://www.pinterest.com/pin/870391065490924089/"


output_location = r"D:\pinterest_download_python\%(title)s.%(ext)s"


os.makedirs('pinterest_download_python', exist_ok=True)



ydl_opt = {
    'outtmpl': output_location,
    'format': 'bestvideo+bestaudio/best',
    'merge_output_format': 'mp4',
}

with yt_dlp.YoutubeDL(ydl_opt) as ydl:
    ydl.download([video_url])