
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
from requests_oauthlib import OAuth2Session

app = FastAPI()


client_id = "<your client key>"
client_secret = "<your client secret>"
authorization_base_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'
api_url = 'https://projectspotify-76glfmoaxq-ew.a.run.app'

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

def get_genre_from_artist_id(id = '', token):
    #get genres from the artist
    artist_url = f'https://api.spotify.com/v1/artists/{id}'

    headers = dict()
    headers["Authorization"] = f"Bearer {token}"
    spotify = requests.get(artist_url, headers = headers)
    if spotify.status_code != 200: 
        print('Not working')
    results = spotify.json()
    result = results['genres']
    if result == []: 
        result = 'No genre sorry'
    return result

@app.get("/", response_class=HTMLResponse)
def web_root(request: Request):

    token = requests.get('/spotify_response').json()['resp']

    # get songs from spotify
    headers = dict()
    headers["Authorization"] = f"Bearer {token}"
    current_user_tracks_url = 'https://api.spotify.com/v1/me/tracks'
    response = requests.get(current_user_tracks_url, headers = headers)
    if response != 200: 
        print('Not working')
    results = response.json()
    songs = []
    for item in results['items']:
        song = {}
        track = item['track']
        tid = track['id']
        song['artist'] = track['artists'][0]['name']
        song['title'] = track['name']

        # getting artist genres
        artist_id = track['artists'][0]['id']
        song['spotify_genre'] = get_genre_from_artist_id(artist_id, token)

        # getting the api prediction
        response = requests.get(f'{api_url}/predict_genre/{tid}')
        if response.status_code == 200:
            prediction = response.json()
            pred = prediction['prediction']
        else: 
            pred = 'Spotify caused an error 😞'
        song['prediction_genre'] = pred
        songs.append(song)

    # render template
    return templates.TemplateResponse("item.html", {"request": request, "songs": songs})


@app.get("/spotify_response")
def spotify_callback(token):
    return {"resp": token}