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
progress_update_active = False
paused = False


#   CHECKING IF THE AUDIO FOLDER HAS THE SEARCHED FILE
def check_file(song, artist, duration_ms):
    mp3_audio_path = f'audio/{song}_{artist}.mp3'    
    if os.path.exists(mp3_audio_path):
        play_audio(mp3_audio_path)
        progress_bar["maximum"] = duration_ms / 1000 / 60
    else:
        download_audio(song, artist)
        play_audio(mp3_audio_path)
        progress_bar["maximum"] = duration_ms / 1000 / 60


# Function to play the selected song
def play_selected(song, artist):
    global paused
    mp3_audio_path = f'audio/{song}_{artist}.mp3'
    if paused:
        resume_playback()
    else:
       play_audio(mp3_audio_path)

# Function to pause the playback
def pause_playback():
    global paused
    paused=True
    pygame.mixer.music.pause()

# Function to resume playback
def resume_playback():
    global paused
    paused = False
    pygame.mixer.music.unpause()
    update_progress()
    

# Function to stop the playback
def stop_playback():
    global progress_update_active
    pygame.mixer.music.stop()
    progress_bar["value"] = 0 
    progress_value_label.config(text="0:00 / 0:00") 
    progress_update_active = False

#   PLAY THE SEARCHED FILE
def play_audio(mp3_audio_path):
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_audio_path)
    pygame.mixer.music.play()
    update_progress()

def select_song(event, song, artist,duration_ms):
    selected_song.set(song)
    selected_artist.set(artist)
    song_duration.set(duration_ms//1000)
    check_file(song, artist,  duration_ms)

def update_progress():
    global paused
    progress_update_active=True
    print("IN DEF UPDATE PROGRESS")
    if progress_update_active and pygame.mixer.music.get_busy() and not paused:
        current_time = pygame.mixer.music.get_pos() // 1000  # Convert to seconds
        total_time = song_duration.get()
        progress_bar["value"] = current_time
        progress_bar["maximum"] = total_time
        progress_label.config(text=f"{selected_artist.get()} - {selected_song.get()}")
        progress_value_label.config(text=f"{current_time // 60}:{current_time % 60:02d} / {total_time // 60}:{total_time % 60:02d}")
        root.after(1000, update_progress)


#   GET PLAYLIST INFO FROM YOUR SPOTIFY ACCOUNT
def get_playlist_info():
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv("SPOTIPY_CLIENT_ID"), client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"), redirect_uri='http://localhost:3000', scope='playlist-read-private'))

        playlist_id = os.getenv("PLAYLISTURL")
        playlist = sp.playlist_tracks(playlist_id)

        songs_and_artists = [(track['track']['name'], track['track']['artists'][0]['name'], track['track']['duration_ms']) for track in playlist['items']]

        result_text.delete(1.0, tk.END)

        for song, artist, duration_ms in songs_and_artists:
            label = tk.Label(result_text, text=f"Play: {song} - {artist}")
            label.bind("<Button-1>", lambda event, s=song, a=artist, d=duration_ms: select_song(event,s,a,d))
            label.pack()
            result_text.insert(tk.END, "\n" * len(songs_and_artists))

root = tk.Tk()
root.title("Spotifly Playlist")

get_button = tk.Button(root, text="Get Playlist", command=get_playlist_info)
get_button.pack()

result_text= tk.Text(root, wrap=tk.WORD, width=50, height=50)
result_text.pack()

#PROGRESS BAR FOR THE SONG
progress_frame = tk.Frame(root)
progress_frame.pack()

progress_label = tk.Label(progress_frame, text=" ")
progress_label.pack(side=tk.LEFT)

progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate", maximum=1)
progress_bar.pack(side=tk.LEFT)

progress_value_label = tk.Label(progress_frame, text="0:00 / 0:00")
progress_value_label.pack(side=tk.LEFT)

# Create a frame for the player controls
player_frame = tk.Frame(root)
player_frame.pack()

# Add play, pause, and stop buttons to the player frame
play_button = tk.Button(player_frame, text="Play", command=lambda: play_selected(selected_song.get(), selected_artist.get()))
pause_button = tk.Button(player_frame, text="Pause", command=pause_playback)
stop_button = tk.Button(player_frame, text="Stop", command=stop_playback)

play_button.pack(side=tk.LEFT)
pause_button.pack(side=tk.LEFT)
stop_button.pack(side=tk.LEFT)

selected_song = tk.StringVar()
selected_artist = tk.StringVar()
song_duration = tk.IntVar()



root.mainloop()
