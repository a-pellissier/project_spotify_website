import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import requests
from os.path import join
from dotenv import load_dotenv
import os

#env_path = join(os.dirname(os.dirname(__file__)),'.env') # ../../.env
load_dotenv(dotenv_path='.env')

api_url = 'https://projectspotify-76glfmoaxq-ew.a.run.app'

def get_own_collection_preview_urls(nb_of_tracks=5, offset=0):
    '''
    Returns list with tids and preview urls
    '''
    scope = "user-library-read"
    SPOTIPY_CLIENT_ID=os.environ.get('SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET=os.environ.get('SPOTIPY_CLIENT_SECRET')
    SPOTIPY_REDIRECT_URI=os.environ.get('SPOTIPY_REDIRECT_URI')

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,client_secret=SPOTIPY_CLIENT_SECRET,redirect_uri=SPOTIPY_REDIRECT_URI,scope=scope))
    results = sp.current_user_saved_tracks(limit=nb_of_tracks, offset=offset)
    song_urls = []
    for idx, item in enumerate(results['items']):
        track = item['track']
        tid = track['id']
        # tid = f'200{idx:03}'
        song_url = track['preview_url']
        song_urls.append((track['artists'][0]['name'],track['name'], tid))
    return song_urls

#st.write(get_own_collection_preview_urls())


if st.button('Make the magic happen'):
    # print is visible in server output, not in the page
    songs = get_own_collection_preview_urls()
    for index, song in enumerate(songs):
        st.write(f'Querying the amazing API for song {song[1]} by {song[0]}')
        response = requests.get(f'{api_url}/predict_genre/{song[2]}')
        if response.status_code == 200:
            prediction = response.json()
            pred = prediction['prediction']
            st.markdown(f'''
                ### The genre is: 
                ### {pred}
                # ''')
        else:
            st.markdown('''## Spotify caused an error 😞''')
else:
    st.write('')


