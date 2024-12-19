import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = spotipy.Spotify(client_credentials_manager=auth_manager)

def playlist_get_songs(playlist_id):
    data=spotify.playlist_items(playlist_id)
    songs=[]
    for item in data['items']:
        songs.append(item['track'])
    return songs

def extract_track(trackOBJ):
    data={
        "name":trackOBJ['name'],
        "artists": [artist['name']for artist in trackOBJ['artists']]
    }
    return data

for song in playlist_get_songs('6GXnlqH82VNc1RCXZnDweq'):
    print(extract_track(song))





