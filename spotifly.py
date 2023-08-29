import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk
from dotenv import load_dotenv
import os
import webbrowser
import requests
import re

load_dotenv()

def play_video(song,artist):
        query = f"{song} {artist}"
        query=query.replace(" ","+")
        search_url = f"https://www.youtube.com/results?search_query={query}"
        response = requests.get(search_url)

        if response.status_code == 200:
            video_id = re.search(r'\/watch\?v=(.{11})', response.text)
        
            if video_id:
                video_url = f"https://www.youtube.com/watch?v={video_id.group(1)}"
                webbrowser.open(video_url)
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
