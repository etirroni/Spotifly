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
        video_ids = re.findall(r'\/watch\?v=(.{11})', response.text)[:5]
        
        for video_id in video_ids:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video = YouTube(video_url)
            
            # Check if the video is age-restricted
            if not video.age_restricted:
                audio_stream = video.streams.filter(only_audio=True, file_extension='webm').order_by('abr').desc().first()
                audio_stream.download(output_path='audio', filename=f'{song}_{artist}.webm')

                webm_audio_path = f'audio/{song}_{artist}.webm'

                # Convert the webm audio to mp3 using pydub
                webm_audio = AudioSegment.from_file(webm_audio_path, format="webm")
                mp3_audio_path = f'audio/{song}_{artist}.mp3'
                webm_audio.export(mp3_audio_path, format="mp3")

                # Clean up: remove the original webm audio file
                os.remove(webm_audio_path)

                max_file_count = 10
                audio_files = sorted(os.listdir('audio'), key=lambda f: os.path.getmtime(os.path.join('audio', f)))
                while len(audio_files) >= max_file_count:
                    oldest_file = audio_files.pop(0)
                    os.remove(os.path.join('audio', oldest_file))

                break  # Exit the loop once a non-age-restricted video is found
            else:
                print(f"Video with ID {video_id} is age-restricted. Trying the next video...")
        else:
            print(f"Video not found")
    else:
        print("Error searching on YouTube")

