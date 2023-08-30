import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk
from pydub import AudioSegment
from dotenv import load_dotenv
from pytube import YouTube
from pydub import AudioSegment
from pydub.playback import play

import os
import requests
import re
import pygame

load_dotenv()
pygame.mixer.init()

def play_video(song,artist):
        query = f"{song} {artist} official audio"
        query=query.replace(" ","+")
        search_url = f"https://www.youtube.com/results?search_query={query}"
        response = requests.get(search_url)

        if response.status_code == 200:
            video_id = re.search(r'\/watch\?v=(.{11})', response.text)
        
            if video_id:
                mp3_audio_path=f'audio/{song}_{artist}.mp3'
                if os.path.exists(mp3_audio_path):
                    pygame.mixer.music.load(mp3_audio_path)
                    pygame.mixer.music.play()
                else:
                    video_url = f"https://www.youtube.com/watch?v={video_id.group(1)}"
                    video = YouTube(video_url)
                    audio_stream = video.streams.filter(only_audio=True, file_extension='webm').order_by('abr').desc().first()
                    audio_stream.download(output_path='audio', filename=f'{song}_{artist}.webm')
                    webm_audio_path = f'audio/{song}_{artist}.webm'
                    webm_audio=AudioSegment.from_file(webm_audio_path, format="webm")
                    webm_audio.export(mp3_audio_path, format="mp3")
                    pygame.mixer.music.load(mp3_audio_path)
                    pygame.mixer.music.play()
                    os.remove(webm_audio_path)                
            else:
                result_text.insert(tk.END, f"No video found for {query}\n")
        else:
            result_text.insert(tk.END, "Error searching on YouTube\n")

def get_playlist_info():
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv("SPOTIPY_CLIENT_ID"), client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"), redirect_uri='http://localhost:3000', scope='playlist-read-private'))

        playlist_id = os.getenv("PLAYLISTURL")
        playlist = sp.playlist_tracks(playlist_id)

        songs_and_artists = [(track['track']['name'], track['track']['artists'][0]['name']) for track in playlist['items']]

        result_text.delete(1.0, tk.END)

        for song, artist in songs_and_artists:
            label = tk.Label(result_text, text=f"Play: {song} - {artist}")
            label.bind("<Button-1>", lambda event, s=song, a=artist: play_video(s, a))
            label.pack()
            result_text.insert(tk.END, "\n" * len(songs_and_artists))

root = tk.Tk()
root.title("Spotifly Playlist")

get_button = tk.Button(root, text="Get Playlist", command=get_playlist_info)
get_button.pack()

result_text= tk.Text(root, wrap=tk.WORD, width=50, height=50)
result_text.pack()

root.mainloop()
