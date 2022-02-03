import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json

#defines what resources we are asking from the spotify user are
scope  = 'playlist-modify-public'
username = '1120707104'

#authenticates the user, so the application can be used
token = SpotifyOAuth(scope=scope,username=username)
spotifyObject = spotipy.Spotify(auth_manager=token)


#create playlist
playlist_name = input('Enter a playlist name:')
playlist_description = input('Enter a playlist description:')

spotifyObject.user_playlist_create(user = username, name= playlist_name, public = True, description = playlist_description)

user_input = ''
user_input = input('Enter a song name:')
list_of_songs = []
while user_input != 'quit':
    results = spotify.search(q=user_input)
    print(results['tracks']['items'][0]['uri'])

    newResults = results ['tracks']['items'][0]['uri']

    #create list of new songs
    list_of_songs.append(newResults)

    #identify id of newest playlist
    prePlaylists = spotify.user_playlists(user=username)
    playlist = prePlaylists['items'][0]['id']
    user_input = input('Enter a song name:')

#add songs
spotify.user_playlist_add_tracks(user = username, playlist_id = playlist, tracks = list_of_songs)
