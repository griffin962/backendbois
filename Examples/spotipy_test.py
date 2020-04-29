import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials

# Function for getting artist image URL
def getArtistImage(artist_name):
    
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    results = spotify.search(q='artist:' + artist_name, type='artist')
    items = results['artists']['items']
    
    if len(items) > 0:
        artist = items[0]
        img = artist['images'][0]['url']
        return img
    
    #if no artist was found
    return None

if __name__ == "__main__":
    