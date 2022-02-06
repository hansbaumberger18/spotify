import numpy as np
import pandas as pd
import seaborn as sns
import spotify_keys as keys
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import cdist
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from collections import defaultdict
import difflib
import streamlit as st

st.set_page_config(page_title="Song Recommendation", layout="wide")

title = "Song Recommendation Engine"
st.title(title)
st.write("First of all, welcome! This is the place where you can customize what you want to listen to based on genre and several key audio features. Try playing around with different settings and listen to the songs recommended by our system!")
st.markdown("##")


df = pd.read_csv('../data/JOINT.csv')

df.drop(columns = ['time_signature'], inplace = True)

# Drop rows containing null values as they aren't a significant number
df.dropna(inplace = True)
df.drop_duplicates(['id'], inplace = True)

#change release_date to datetime
df['release_year'] = df['release_date'].apply(lambda x: x.split('-')[0])
df.drop(columns = ['release_date'], inplace = True)

#Change duration in ms to seconds and drop duration_ms column
df['duration'] = df['duration_ms'].apply(lambda x: round(x/1000))
df.drop(columns = ['duration_ms'], inplace = True)

#Scaling Data.

df_numerical = df.select_dtypes(np.number)

scaler = StandardScaler().fit(df_numerical) #Only Scale numerical columns
scaled_data = scaler.transform(df_numerical)

features_df = pd.DataFrame(scaled_data)
features_df.head()

km = KMeans(n_clusters = 10).fit(features_df)
#tsne_df['cluster'] = pd.Categorical(km.labels_)

client_id = keys.SPOTIFY_CLIENT_ID
client_secret = keys.SPOTIFY_CLIENT_SECRET

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

def find_song(lista):
    inp = pd.DataFrame()
    for (title, artist) in lista:
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
        inp = pd.concat([inp, df])
    return inp



#while len(list_of_songs)<2:
input_first_song = st.text_input('Enter first song name:')
input_first_artist = st.text_input('Enter first artist name:')
input_second_song = st.text_input('Enter second song name:')
input_second_artist = st.text_input('Enter second artist name:')
list_of_songs = [(input_first_song,input_first_artist), (input_second_song,input_second_artist)]

y = find_song(list_of_songs)

#scaled_y = scaler.transform(np.array(y).reshape(1,-1))
y.drop(columns = ['speechiness'], inplace = True)
y = y.select_dtypes(np.number).mean()

scaled_y = scaler.transform(np.array(y).reshape(1,-1))

def recommend_songs(feats_df, track_data, y, n):

    feats_df['cluster'] = pd.Categorical(km.labels_)
    user_cluster = km.predict(y)

    df_slice = feats_df[feats_df['cluster']==user_cluster[0]]
    df_slice = df_slice.drop(['cluster'], axis=1)
    indices = feats_df[feats_df['cluster']==user_cluster[0]].reset_index()['index'].to_numpy()

    scaled_data = df_slice.to_numpy()

    simi = cdist(scaled_data, y, metric='cosine').argsort(axis=None)[:n]

    rec_songs = track_data.iloc[simi]

    return rec_songs[['title', 'all_artists']]

st.dataframe(data=recommend_songs(feats_df = features_df , track_data = df, y = scaled_y, n = 10), width=None, height=None)
