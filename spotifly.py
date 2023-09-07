import spotipy
import tkinter as tk
import os
import pygame
from PIL import Image,ImageTk
from spotipy.oauth2 import SpotifyOAuth
from mutagen.mp3 import MP3
from tkinter import ttk
from dotenv import load_dotenv

from spotiflyDownload import download_audio
import styles 


load_dotenv()
pygame.mixer.init()

# GLOBBAL VARIABLES
progress_update_active = False
paused = False
current_song_index = -1
song_duration = 0
update_progress_id = None 
image_path = "assets/SpotiFly.jpg"
song_on_player = ""


#   CHECKING IF THE AUDIO FOLDER HAS THE SEARCHED FILE
def check_file(song, artist):
    global song_duration
    mp3_audio_path = f'audio/{song}_{artist}.mp3'    
    if os.path.exists(mp3_audio_path):
        song_duration= int(MP3(mp3_audio_path).info.length)
        progress_bar["value"] = 0
        progress_bar["maximum"] = song_duration
        play_audio(mp3_audio_path)
        
    else:
        download_audio(song, artist)
        song_duration= int(MP3(mp3_audio_path).info.length)
        progress_bar["value"] = 0
        progress_bar["maximum"] = song_duration
        play_audio(mp3_audio_path)
        
# Play button
def play_selected(song, artist):
    global progress_update_active, paused
    mp3_audio_path = f'audio/{song}_{artist}.mp3'
    if paused:
        resume_playback()
    else:
       play_audio(mp3_audio_path)

# Pause button
def pause_playback():
    global paused, progress_update_active
    if progress_update_active:
        progress_update_active=False
        print("ON PAUSE")
        paused=True
        pygame.mixer.music.pause()


# Resume button (play button when song is paused)
def resume_playback():
    global paused, progress_update_active
    print("resume function")
    if paused:
        paused = False
        pygame.mixer.music.unpause()
        progress_update_active = True  # Set progress_update_active back to True
        update_progress()
    
# stop button
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

# FUNCTION AFTER CLICKING SONG IN THE PLAYLIST
def select_song(event, song, artist, songs_and_artists):
    global current_song_index, song_duration, progress_update_active
    progress_update_active = False
    current_song_index = songs_and_artists.index((song, artist))
    selected_song.set(song)
    selected_artist.set(artist)
    check_file(song, artist)



# CALLED WHEN SONG ENDS OR "NEXT" BUTTON IS PRESSED
def play_next_song():
    global current_song_index, progress_update_active, song_duration
    if current_song_index < len(songs_and_artists) - 1:
        progress_update_active = False
        current_song_index += 1
        song, artist = songs_and_artists[current_song_index]
        mp3_audio_path = f'audio/{song}_{artist}.mp3'
        if not os.path.exists(mp3_audio_path):
            download_audio(song, artist)    
        song_duration= int(MP3(mp3_audio_path).info.length)
        progress_bar["value"] = 0
        progress_bar["maximum"] = song_duration
        selected_song.set(song)  
        selected_artist.set(artist) 
        play_audio(mp3_audio_path)      
   
# CALLED WHEN "PREVIOUS" BUTTON IS PRESSED
def play_previous_song():
    global current_song_index, progress_update_active, song_duration
    if current_song_index > 0:
        progress_update_active = False
        current_song_index -= 1
        song, artist = songs_and_artists[current_song_index]
        mp3_audio_path = f'audio/{song}_{artist}.mp3'
        if not os.path.exists(mp3_audio_path):
            download_audio(song, artist)
        song_duration = int(MP3(mp3_audio_path).info.length)
        progress_bar["value"] = 0
        progress_bar["maximum"] = song_duration
        selected_song.set(song)  
        selected_artist.set(artist) 
        play_audio(mp3_audio_path)
   
# FUNCTION TO UPDATE THE PROGRESS BAR
def update_progress():
    global paused, progress_update_active, song_duration, update_progress_id 
    if progress_update_active and not paused:
        current_time = pygame.mixer.music.get_pos() // 1000  # Convert to seconds
        total_time = song_duration
        #last_current_times.append(current_time)
        #last_current_times = last_current_times[-3:]
        #print("last_current_times values: ", last_current_times)
        print("song duration in update_progress: ",total_time)
        progress_bar["value"] = current_time
        progress_bar["maximum"] = total_time 
        print(current_time, " and ", total_time)
        progress_label.config(text=f"♫ Now Playing: {selected_artist.get()} - {selected_song.get()}")
        progress_value_label.config(text=f"{current_time // 60}:{current_time % 60:02d} / {total_time // 60}:{total_time % 60:02d}")
        #if len(set(last_current_times))==1:
        if total_time-1==current_time:
            progress_update_active = False 
            play_next_song()
        else:
            update_progress_id = root.after(1000, update_progress)
    else:
        update_progress_id = None
        print("upodate_progress end")

#   GET PLAYLIST INFO FROM YOUR SPOTIFY ACCOUNT
def get_playlist_info():
        global songs_and_artists
        def on_enter(event):
            label = event.widget
            label.configure(background="blue")
        def on_leave(event):
            label = event.widget
            label.configure(background="black")
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv("SPOTIPY_CLIENT_ID"), client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"), redirect_uri='http://localhost:3000', scope='playlist-read-private'))
        playlist_id = os.getenv("PLAYLISTURL")
        playlist = sp.playlist_tracks(playlist_id)
        songs_and_artists = [(track['track']['name'], track['track']['artists'][0]['name']) for track in playlist['items']]
        
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        for song, artist in songs_and_artists:

                label = tk.Label(scrollable_frame,background=styles.BUTTON_BG, font=styles.CUSTOM_FONT_SMALL, fg=styles.BUTTON_TEXT_COLOR, text=f"{song} - {artist}" )
                label.bind("<Button-1>", lambda event, s=song, a=artist, sa=songs_and_artists: select_song(event,s,a,sa))
                label.bind("<Enter>", on_enter)
                label.bind("<Leave>", on_leave)
                label.pack()
        scrollable_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
                
               

           
       
# GUI SETTINGS DOWN BELOW

root = tk.Tk()
root.title("Spotifly Playlist")
root.geometry("535x900")

selected_song = tk.StringVar()
selected_artist = tk.StringVar()

bg_image = Image.open(image_path)
bg_photo = ImageTk.PhotoImage(bg_image)

background_label = tk.Label(root, bg="black")
background_label.place(relwidth=1, relheight=1)

get_button = tk.Button(root, text="Get Playlist",background=styles.BG_COLOR, font=styles.CUSTOM_FONT, fg=styles.BUTTON_TEXT_COLOR, command=get_playlist_info)
get_button.place(relx=0.25, rely=0.05, relwidth=0.5)

# AREA FOR THE PLAYLIST
result_frame = tk.Frame(root, background=styles.BUTTON_BG, bd=0, highlightthickness=0)
result_frame.place(relx=0.25, rely=0.1, relwidth=0.5)

canvas = tk.Canvas(result_frame, background=styles.BUTTON_BG, bd=0, highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

scroll_y = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scroll_y.pack(side="right", fill="y")

scrollable_frame = tk.Frame(canvas, background=styles.BUTTON_BG)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scroll_y.set)

# FRAME FOR PROGRESS-BAR 
progress_frame = tk.Frame(root, background=styles.BUTTON_BG)
progress_frame.place(relx=0.1, rely=0.7, relwidth=0.8)


# PROGRESS BAR FOR THE SONG
progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate", maximum=1)
progress_bar.pack(side=tk.LEFT)

progress_value_label = tk.Label(progress_frame, text="0:00 / 0:00", background=styles.BUTTON_BG, font=styles.CUSTOM_FONT,fg=styles.BUTTON_TEXT_COLOR)
progress_value_label.pack(side=tk.LEFT)

# ARTIST/SONG info FRAME
song_frame = tk.Frame(root, background=styles.BUTTON_BG)
song_frame.place(relx=0.1, rely=0.8, relwidth=0.8)


progress_label = tk.Label(song_frame, text="", background=styles.BUTTON_BG, font=styles.CUSTOM_FONT_SMALL, fg=styles.BUTTON_TEXT_COLOR)
progress_label.pack(side=tk.LEFT)

# FRAME FOR PLAYER CONTROLS
player_frame = tk.Frame(root, background=styles.BUTTON_BG)
player_frame.place(relx=0.1, rely=0.85, relwidth=0.8)

# PLAYER BUTTONS
play_button = tk.Button(player_frame, text="▶", width=5 ,font=styles.CUSTOM_FONT, bg=styles.GREEN,fg=styles.BUTTON_TEXT_COLOR, command=lambda: play_selected(selected_song.get(), selected_artist.get()))
pause_button = tk.Button(player_frame, text="⏸︎", width=5 ,font=styles.CUSTOM_FONT, bg=styles.GREEN,fg=styles.BUTTON_TEXT_COLOR, command=pause_playback)
stop_button = tk.Button(player_frame, text="■", width=5 ,font=styles.CUSTOM_FONT, bg=styles.RED,fg=styles.BUTTON_TEXT_COLOR, command=stop_playback)
next_button = tk.Button(player_frame, text="⏩", width=5 ,font=styles.CUSTOM_FONT, bg=styles.BLUE,fg=styles.BUTTON_TEXT_COLOR, command=play_next_song)
previous_button = tk.Button(player_frame, text="⏪", width=7 ,font=styles.CUSTOM_FONT, bg=styles.BLUE,fg=styles.BUTTON_TEXT_COLOR, command=play_previous_song)

play_button.pack(side=tk.LEFT, padx=(5,10))
pause_button.pack(side=tk.LEFT, padx=5)
stop_button.pack(side=tk.LEFT, padx=5)
next_button.pack(side=tk.LEFT, padx=5)
previous_button.pack(side=tk.LEFT,padx=(5,10))


root.mainloop()