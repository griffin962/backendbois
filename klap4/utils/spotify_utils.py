import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials


spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


# Function for getting artist image URL
def getArtistImage(artist_name):
        
    if len(artist_name) > 1:
        name = ' '.join(sys.argv[1:])
    else:
        name = artist_name
    
    results = spotify.search(q='artist:' + artist_name, type='artist')
    items = results['artists']['items']
    
    if len(items) > 0:
        artist = items[0]
        img = artist['images'][0]['url']
        return img
    
    #if no artist was found
    return None


# Function for getting related artists (for a given artist)
def getRelatedArtists(artist_name):
    results = spotify.search(q='artist:' + artist_name, type="artist")
    items = results['artists']['items']
    
    if len(items) > 0:
        artist = items[0]
        id = artist['id']
        artists = spotify.artist_related_artists(id)
        return artists
    
    return None


# Function for getting album image
def getAlbumCover(album_name, artist_name):
    query = 'album:{0}&20artist:{1}'.format(album_name, artist_name)
    results = spotify.search(q=query, type='album')
    items = results['albums']['items']
    
    if len(items) > 0:
        album = items[0]
        img = album['images'][0]['url']
        return img

    return None