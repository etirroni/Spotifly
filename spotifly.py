import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk
from tkinter import ttk
from dotenv import load_dotenv

from spotiflyDownload import download_audio

import os
import pygame

load_dotenv()
pygame.mixer.init()


#   CHECKING IF THE AUDIO FOLDER HAS THE SEARCHED FILE
def check_file(song, artist):
    mp3_audio_path = f'audio/{song}_{artist}.mp3'    
    if os.path.exists(mp3_audio_path):
        play_audio(mp3_audio_path)
    else:
        download_audio(song, artist)
        play_audio(mp3_audio_path)
# Function to play the selected song
def play_selected(song, artist):
    mp3_audio_path = f'audio/{song}_{artist}.mp3'
    play_audio(mp3_audio_path)

# Function to pause the playback
def pause_playback():
    pygame.mixer.music.pause()

# Function to resume playback
def resume_playback():
    pygame.mixer.music.unpause()

# Function to stop the playback
def stop_playback():
    pygame.mixer.music.stop()
#   PLAY THE SEARCHED FILE
def play_audio(mp3_audio_path):
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_audio_path)
    pygame.mixer.music.play()

def select_song(event, song, artist):
    selected_song.set(song)
    selected_artist.set(artist)
    check_file(song, artist)



#   GET PLAYLIST INFO FROM YOUR SPOTIFY ACCOUNT
def get_playlist_info():
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv("SPOTIPY_CLIENT_ID"), client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"), redirect_uri='http://localhost:3000', scope='playlist-read-private'))

        playlist_id = os.getenv("PLAYLISTURL")
        playlist = sp.playlist_tracks(playlist_id)

        songs_and_artists = [(track['track']['name'], track['track']['artists'][0]['name']) for track in playlist['items']]

        result_text.delete(1.0, tk.END)

        for song, artist in songs_and_artists:
            label = tk.Label(result_text, text=f"Play: {song} - {artist}")
            label.bind("<Button-1>", lambda event, s=song, a=artist: select_song(event,s, a))
            label.pack()
            result_text.insert(tk.END, "\n" * len(songs_and_artists))

root = tk.Tk()
root.title("Spotifly Playlist")

get_button = tk.Button(root, text="Get Playlist", command=get_playlist_info)
get_button.pack()

result_text= tk.Text(root, wrap=tk.WORD, width=50, height=50)
result_text.pack()

#PROGRESS BAR FOR THE SONG
progress_bar=ttk.Progressbar(root, orient="horizontal",length=400, mode="determinate")
progress_bar.pack()

# Create a frame for the player controls
player_frame = tk.Frame(root)
player_frame.pack()

# Add play, pause, and stop buttons to the player frame
play_button = tk.Button(player_frame, text="Play", command=lambda: play_selected(selected_song.get(), selected_artist.get()))
pause_button = tk.Button(player_frame, text="Pause", command=pause_playback)
resume_button = tk.Button(player_frame, text="Resume", command=resume_playback)
stop_button = tk.Button(player_frame, text="Stop", command=stop_playback)

play_button.pack(side=tk.LEFT)
pause_button.pack(side=tk.LEFT)
resume_button.pack(side=tk.LEFT)
stop_button.pack(side=tk.LEFT)

selected_song = tk.StringVar()
selected_artist = tk.StringVar()

root.mainloop()
