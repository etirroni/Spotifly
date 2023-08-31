from pydub import AudioSegment
import os
from pytube import YouTube
import requests
import re


def download_audio(song, artist):
    query = f"{song} {artist} official audio"
    query = query.replace(" ", "+")
    search_url = f"https://www.youtube.com/results?search_query={query}"
    response = requests.get(search_url)

    if response.status_code == 200:
        video_id = re.search(r'\/watch\?v=(.{11})', response.text)
        print(video_id)

        if video_id:
            video_url = f"https://www.youtube.com/watch?v={video_id.group(1)}"
            video = YouTube(video_url)
            audio_stream = video.streams.filter(only_audio=True, file_extension='webm').order_by('abr').desc().first()
            audio_stream.download(output_path='audio', filename=f'{song}_{artist}.webm')

            webm_audio_path = f'audio/{song}_{artist}.webm'

            # Convert the webm audio to mp3 using pydub
            webm_audio = AudioSegment.from_file(webm_audio_path, format="webm")
            mp3_audio_path = f'audio/{song}_{artist}.mp3'
            webm_audio.export(mp3_audio_path, format="mp3")

            # Clean up: remove the original webm audio file
            os.remove(webm_audio_path)

            max_file_count=10
            audio_files= sorted(os.listdir('audio'), key=lambda f: os.path.getmtime(os.path.join('audio', f)))
            while len(audio_files) >= max_file_count:
                oldest_file = audio_files.pop(0)
                os.remove(os.path.join('audio', oldest_file))
        else:
            print(f"No video found for {query}\n")
    else:
        print("Error searching on YouTube\n")