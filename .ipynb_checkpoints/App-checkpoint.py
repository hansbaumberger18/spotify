#https://towardsdatascience.com/build-a-song-recommendation-system-using-streamlit-and-deploy-on-heroku-375a57ce5e85



import os
import numpy as np
import pandas as pd

import seaborn as sns
import plotly.express as px 
import matplotlib.pyplot as plt


from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.metrics import euclidean_distances
from scipy.spatial.distance import cdist

import warnings
warnings.filterwarnings("ignore")

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from collections import defaultdict


from sklearn.metrics import euclidean_distances
from scipy.spatial.distance import cdist
import difflib



###################################################################
import streamlit as st

st.set_page_config(page_title="Song Recommendation", layout="wide")

title = "Song Recommendation Engine"
st.title(title)
st.write("First of all, welcome! This is the place where you can customize what you want to listen to based on genre and several key audio features. Try playing around with different settings and listen to the songs recommended by our system!")
st.markdown("##")


####################################################################
data = pd.read_csv('./data/JOINT.csv')

data.drop(columns = ['time_signature'], inplace = True)

# Drop rows containing null values as they aren't a significant number
data.dropna(inplace = True)
data.drop_duplicates(['id'], inplace = True)

#change release_date to datetime
data['release_year'] = data['release_date'].apply(lambda x: x.split('-')[0])
data.drop(columns = ['release_date'], inplace = True)

#Change duration in ms to seconds and drop duration_ms column
data['duration'] = data['duration_ms'].apply(lambda x: round(x/1000))
data.drop(columns = ['duration_ms'], inplace = True)



#######################################################################
song_cluster_pipeline = Pipeline([('scaler', StandardScaler()), 
                                  ('kmeans', KMeans(n_clusters=4, 
                                   verbose=False, n_jobs=4))
                                 ], verbose=False)

X = data.select_dtypes(np.number)
number_cols = list(X.columns)
song_cluster_pipeline.fit(X)
song_cluster_labels = song_cluster_pipeline.predict(X)
data['cluster_label'] = song_cluster_labels

#######################################################################
SPOTIFY_CLIENT_ID = 'daf844afde2c4b25840254841b7952f9'
SPOTIFY_CLIENT_SECRET = 'd82684f896274fae917f37a1ff88b2fb'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

def find_song(title, artist):
    song_data = defaultdict()
    #results = sp.search(q= 'track: {}'.format(title), limit=1)
    results = sp.search(q = 'track: {} artist: {}'.format(title, artist), limit=1, offset=0, type='track')
    if results['tracks']['items'] == []:
        return None

    results = results['tracks']['items'][0]
    track_id = results['id']
    audio_features = sp.audio_features(track_id)[0]

    song_data['title'] = [title]
    song_data['artist'] = [artist]
    song_data['duration_ms'] = [results['duration_ms']]
    song_data['popularity'] = [results['popularity']]

    for key, value in audio_features.items():
        #key = feature and value = value of feature
        song_data[key] = value
    
    df = pd.DataFrame(song_data)
    
    #CAMBIOS DE MI FEATURE ENGINEERING    
    df.drop(columns = ['time_signature'], inplace = True)

    # Drop rows containing null values as they aren't a significant number
    df.dropna(inplace = True)
    df.drop_duplicates(['id'], inplace = True)

    #Change duration in ms to seconds and drop duration_ms column
    df['duration'] = df['duration_ms'].apply(lambda x: round(x/1000))
    df.drop(columns = ['duration_ms'], inplace = True)
        
    return df

#######################################################################

#Song_list must be a list of tuples --> [('title', 'artist')]
def get_mean_vector(song_list):
    
    song_vectors = []
    
    for song in song_list:
        song_data = find_song(song[0], song[1])
        if song_data is None:
            print('Warning: {} from {} does not exist in Spotify or in database'.format(song['title'], song['artist']))
            continue
        song_vector = song_data[number_cols].values
        song_vectors.append(song_vector)  
    
    song_matrix = np.array(list(song_vectors))
    return np.mean(song_matrix, axis=0)

#######################################################################

def recommend_songs(song_list, tracks_data=data, n_songs=10):
    
    metadata_cols = ['title', 'all_artists']
    
    song_center = get_mean_vector(song_list)
    scaler = song_cluster_pipeline.steps[0][1] #Instantiates StandardScaler()
    scaled_data = scaler.transform(tracks_data[number_cols])
    scaled_song_center = scaler.transform(song_center.reshape(1, -1))
    distances = cdist(scaled_song_center, scaled_data, 'cosine')
    index = list(np.argsort(distances)[:, :n_songs][0])
    
    rec_songs = tracks_data.iloc[index]
    return rec_songs[['title', 'all_artists']]

#######################################################################

user_input_song = st.text_input('Enter song name:')
user_input_artist = st.text_input('Enter artist name:')

#input_song = input('Enter song name:')
#input_artist = input('Enter artist name:')
list_of_songs = []
list_of_songs.append((user_input_song, user_input_artist))

recommend_songs(song_list = list_of_songs)

