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
current_song_index = -1
song_duration = 0
update_progress_id = None 
last_current_times = [0,0,0]

def show_saved_lists():
    print(" ")
def save_playlist():
    print("saved!")

#   CHECKING IF THE AUDIO FOLDER HAS THE SEARCHED FILE
def check_file(song, artist, duration_ms):
    mp3_audio_path = f'audio/{song}_{artist}.mp3'    
    if os.path.exists(mp3_audio_path):
        play_audio(mp3_audio_path)
        
    else:
        download_audio(song, artist)
        play_audio(mp3_audio_path)
        
# Function to play the selected song
def play_selected(song, artist):
    global progress_update_active, paused
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
    global paused, progress_update_active
    paused = False
    pygame.mixer.music.unpause()
    progress_update_active = True  # Set progress_update_active back to True
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
    global progress_update_active, update_progress_id
    progress_update_active = True
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_audio_path)
    pygame.mixer.music.play()
    if update_progress_id is not None:
        root.after_cancel(update_progress_id)
    
    # Schedule the update_progress() function to start updating the progress bar
    update_progress_id = root.after(1000, update_progress)

def select_song(event, song, artist,duration_ms, songs_and_artists):
    global current_song_index, song_duration, progress_update_active
    progress_update_active = False
    current_song_index = songs_and_artists.index((song, artist, duration_ms))
    selected_song.set(song)
    selected_artist.set(artist)
    song_duration=duration_ms//1000
    check_file(song, artist,  duration_ms)

def play_next_song():
    global current_song_index, progress_update_active, song_duration
    progress_update_active = False
    if current_song_index < len(songs_and_artists) - 1:
        current_song_index += 1
        song, artist, duration_ms = songs_and_artists[current_song_index]
        mp3_audio_path = f'audio/{song}_{artist}.mp3'
        if not os.path.exists(mp3_audio_path):
            download_audio(song, artist)    
        song_duration=duration_ms//1000
        print("song_duration in play_next_song: ",song_duration)
        progress_bar["value"] = 0
        progress_bar["maximum"] = song_duration
        play_audio(mp3_audio_path)      
    else:
        
        print("End of playlist")

def update_progress():
    global paused, progress_update_active, song_duration, update_progress_id, last_current_times
    if progress_update_active and not paused:
        current_time = pygame.mixer.music.get_pos() // 1000  # Convert to seconds
        total_time = song_duration
        last_current_times.append(current_time)
        last_current_times = last_current_times[-3:]
        print("last_current_times values: ", last_current_times)
        print("song duration in update_progress: ",total_time)
        progress_bar["value"] = current_time
        progress_bar["maximum"] = total_time
        print(current_time, " and ", total_time)
        progress_label.config(text=f"{selected_artist.get()} - {selected_song.get()}")
        progress_value_label.config(text=f"{current_time // 60}:{current_time % 60:02d} / {total_time // 60}:{total_time % 60:02d}")
        if len(set(last_current_times))==1:
            progress_update_active = False 
            play_next_song()
        else:
            update_progress_id = root.after(1000, update_progress)
    else:
        update_progress_id = None

#   GET PLAYLIST INFO FROM YOUR SPOTIFY ACCOUNT
def get_playlist_info():
        global songs_and_artists
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv("SPOTIPY_CLIENT_ID"), client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"), redirect_uri='http://localhost:3000', scope='playlist-read-private'))

        playlist_id = os.getenv("PLAYLISTURL")
        playlist = sp.playlist_tracks(playlist_id)

        songs_and_artists = [(track['track']['name'], track['track']['artists'][0]['name'], track['track']['duration_ms']) for track in playlist['items']]

        result_text.delete(1.0, tk.END)

        for song, artist, duration_ms in songs_and_artists:
            label = tk.Label(result_text, text=f"Play: {song} - {artist}")
            label.bind("<Button-1>", lambda event, s=song, a=artist, d=duration_ms, sa=songs_and_artists: select_song(event,s,a,d,sa))
            label.pack()
            result_text.insert(tk.END, "\n" * len(songs_and_artists))
        save_playlist_button=tk.Button(root, text="Save This Playlist", command=save_playlist)
        save_playlist_button()
        

root = tk.Tk()
root.title("Spotifly Playlist")

my_playlists_button = tk.Button(root, text="Saved Playlists", command=show_saved_lists)
my_playlists_button.pack()
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
#song_duration = tk.IntVar()



root.mainloop()