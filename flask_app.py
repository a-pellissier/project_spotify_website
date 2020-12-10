import requests
from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, render_template
from flask.json import jsonify
import os
from os.path import join
from dotenv import load_dotenv

from flask_cors import CORS
app = Flask(__name__)
CORS(app)

load_dotenv(dotenv_path='.env')

scope = "user-library-read"
SPOTIPY_CLIENT_ID=os.environ.get('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET=os.environ.get('SPOTIPY_CLIENT_SECRET')

# This allows us to use a plain HTTP callback
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

app.secret_key = os.urandom(24)
app.run(debug=True)


from jinja2 import Environment, FileSystemLoader
e = Environment(loader=FileSystemLoader('templates/'))

# This information is obtained upon registration of a new Spotify
client_id = SPOTIPY_CLIENT_ID
client_secret = SPOTIPY_CLIENT_SECRET
authorization_base_url = 'https://accounts.spotify.com/authorize?'
token_url = 'https://accounts.spotify.com/api/token'
api_url = 'https://projectspotify-76glfmoaxq-ew.a.run.app'

base_redirect_uri = 'https://lewagonmusicproject.herokuapp.com'

@app.route("/")
def demo():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    spotify = OAuth2Session(client_id, redirect_uri=f'{base_redirect_uri}/callback', scope = 'user-library-read')
    authorization_url, state = spotify.authorization_url(authorization_base_url)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@app.route("/callback", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    spotify = OAuth2Session(client_id, state=session['oauth_state'], redirect_uri = f'{base_redirect_uri}/callback')
    token = spotify.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)

    # At this point you can fetch protected resources but lets save
    # the token and show how this is done from a persisted token
    # in /profile.
    session['oauth_token'] = token

    return redirect(url_for('.profile'))


@app.route("/profile", methods=["GET"])
def profile():
    """Fetching a protected resource using an OAuth 2 token.
    """
    spotify = OAuth2Session(client_id, token=session['oauth_token'])
    current_user_tracks_url = 'https://api.spotify.com/v1/me/tracks?limit=2'

    def get_genre_from_artist_id(id): 
        artist_url = f'https://api.spotify.com/v1/artists/{id}'
        artist = spotify.get(f'{artist_url}').json()
        result = artist['genres']
        if result == []: 
            result = 'No genre sorry'
        else: 
            result = ', '.join([item.capitalize() for item in result])
        return result


    results = spotify.get(f'{current_user_tracks_url}').json()
    # response = jsonify(spotify.get(f'{current_user_tracks_url}').json())
    songs = []
    for item in results['items']:
        song = {}
        track = item['track']
        tid = track['id']
        song['artist'] = track['artists'][0]['name']
        song['title'] = track['name']

        # getting artist genres
        artist_id = track['artists'][0]['id']
        song['spotify_genre'] = get_genre_from_artist_id(artist_id)

        # getting the api prediction
        response = requests.get(f'{api_url}/predict_genre/{tid}')
        if response.status_code in range(200,299):
            prediction = response.json()
            pred = prediction['prediction']
        else: 
            pred = 'Spotify caused an error 😞'
        song['prediction_genre'] = pred
        songs.append(song)

    # render template
    return render_template("item.html", request = request, songs= songs)
    return jsonify(songs)
    # return templates.TemplateResponse("item.html", {"request": request, "songs": songs})


# @app.get("/", response_class=HTMLResponse)
# def web_root(request: Request):

#     token = requests.get('/spotify_response').json()['resp']

#     # get songs from spotify
#     headers = dict()
#     headers["Authorization"] = f"Bearer {token}"
#     current_user_tracks_url = 'https://api.spotify.com/v1/me/tracks'


    
