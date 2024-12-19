import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = spotipy.Spotify(client_credentials_manager=auth_manager)


lz_uri = 'spotify:artist:36QJpDe2go2KgaRleHCDTp'  

results = spotify.artist_top_tracks(lz_uri)
for track in results['tracks']:
    print(f"Track: {track['name']} - Preview URL: {track['preview_url']}")




