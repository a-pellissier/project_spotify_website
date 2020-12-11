import requests
from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, render_template
from flask.json import jsonify
from pprint import pformat
from time import time
import os
import json
from os.path import join
from dotenv import load_dotenv
from requests.structures import CaseInsensitiveDict

from flask_cors import CORS
app = Flask(__name__)
CORS(app)

load_dotenv(dotenv_path='.env')


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
refresh_url = token_url

scope = ['user-library-read', 'playlist-modify-public', 'playlist-modify-private', 'user-read-email', 'user-read-private']

base_redirect_uri = 'http://earworm.fr'


# base_redirect_uri = 'http://localhost:5000'

@app.route("/")
def website():
    """"""
    return """
    <head>

    <title>🎵 Spotify 🎵</title>
    <link rel="stylesheet" href="static/styles.css">

    </head>
    <body>
    <div class="content">
    <h1>Welcome to 'Le Wagon roule sur Spotify'</h1>
    <h2> Do you want to test our AMAZING API 💣 ? </h2>
    <p><br></p>
    <center><input class="styled" type=button onclick=window.location.href='/authentification'; value= "👉 Authentificate on Spotify 👈" /> </center>
    <p><br></p>
    <center><input class="styled" type=button onclick=window.location.href='/profile'; value= "👉 I am already authentified !👈" /> </center>
    </div>
    </body>
    
    """



@app.route("/authentification")
def authentification():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    spotify = OAuth2Session(client_id, redirect_uri=f'{base_redirect_uri}/callback', scope = scope)
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

    return redirect(url_for('.menu'))
    # return redirect(url_for('.profile'))


@app.route("/menu", methods=["GET"])
def menu():
    if 'oauth_token' not in session.keys():
        return redirect(url_for('.authentification'))
    """"""
    return """
    <head>

    <title>🎵 Spotify 🎵</title>
    <link rel="stylesheet" href="static/styles.css">

    </head>
    <body>
    <div class="content">
    <h1>Cool you're logged in now ! </h1>
    <h2> Querying the amazing API to predict the genre of your last three liked songs on Spotify... </h2>
    <center><input class="styled" type=button onclick=window.location.href='/profile'; value= "👉 Click here 👈" /> </center>
    </div>
    </body>
    """

# <pre>
# %s
# </pre>
# """ % pformat(session['oauth_token'], indent=4)


@app.route("/profile", methods=["GET"])
def profile():
    """Fetching a protected resource using an OAuth 2 token.
    """
    if 'oauth_token' not in session.keys():
        return redirect(url_for('.authentification'))
        
    spotify = OAuth2Session(client_id, token=session['oauth_token'])
    current_user_tracks_url = 'https://api.spotify.com/v1/me/tracks?limit=3'

    def get_genre_from_artist_id(id): 
        artist_url = f'https://api.spotify.com/v1/artists/{id}'
        artist = spotify.get(f'{artist_url}').json()
        result = artist['genres']
        if result == []: 
            result = 'No genre sorry'
        else: 
            result = ', '.join([item.capitalize() for item in result])
        return result

    gifs = {
        'Classic':'https://giphy.com/embed/YRcDta67pkig6wPoip',
        'Rock':'https://giphy.com/embed/ifCT1dv4jfnSo', 
        'Hip-Hop':'https://giphy.com/embed/fpjdKdw0YwjHa',
        'Jazz':'https://giphy.com/embed/CpfSSEsP7EHza',
        'Pop':'https://giphy.com/embed/iI5slsPoBRFgk',
        'Electronic':'https://giphy.com/embed/aUhEBE0T8XNHa',
        'No prediction, sorry baby boy':'https://giphy.com/embed/d2lcHJTG5Tscg'
    }

    results = spotify.get(f'{current_user_tracks_url}').json()

    # response = jsonify(spotify.get(f'{current_user_tracks_url}').json())
    songs = []
    for item in results['items']:
        song = {}
        track = item['track']
        tid = track['id']
        song['artist'] = track['artists'][0]['name']
        song['title'] = track['name']
        song['id'] = tid
        
 
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
        # pred = 'later'
        song['prediction_genre'] = pred
        song['link'] = f"/classify/{song['prediction_genre']}/{song['id']}"
        song['gif'] = gifs[song['prediction_genre']]
        songs.append(song)

    
    # render template
    return render_template("item.html", request = request, songs= songs)
    return jsonify(songs)
    # return templates.TemplateResponse("item.html", {"request": request, "songs": songs})


@app.route("/automatic_refresh", methods=["GET"])
def automatic_refresh():
    """Refreshing an OAuth 2 token using a refresh token.
    """
    token = session['oauth_token']

    # We force an expiration by setting expired at in the past.
    # This will trigger an automatic refresh next time we interact with
    # Googles API.
    token['expires_at'] = time() - 10

    extra = {
        'client_id': client_id,
        'client_secret': client_secret,
    }

    def token_updater(token):
        session['oauth_token'] = token

    spotify = OAuth2Session(client_id,
                           token=token,
                           auto_refresh_kwargs=extra,
                           auto_refresh_url=refresh_url,
                           token_updater=token_updater)

    # Trigger the automatic refresh
    jsonify(spotify.get('https://api.spotify.com/v1/me/tracks?limit=2').json())
    return jsonify(session['oauth_token'])


@app.route("/manual_refresh", methods=["GET"])
def manual_refresh():
    """Refreshing an OAuth 2 token using a refresh token.
    """
    token = session['oauth_token']

    extra = {
        'client_id': client_id,
        'client_secret': client_secret,
    }

    spotify = OAuth2Session(client_id, token=token)
    session['oauth_token'] = spotify.refresh_token(refresh_url, **extra)
    return jsonify(session['oauth_token'])

@app.route("/validate", methods=["GET"])
def validate():
    """Validate a token with the OAuth provider Spotify.
    """
    token = session['oauth_token']

    # Defined at https://developers.google.com/accounts/docs/OAuth2LoginV1#validatingtoken
    validate_url = ('https://api.spotify.com/v1/me/tracks?limit=2'
                    'access_token=%s' % token['access_token'])

    # No OAuth2Session is needed, just a plain GET request
    return jsonify(requests.get(validate_url).json())


# @app.route("/classify/<genre>/<track_id>", methods=["GET"])
# def classify(genre, track_id):
#     """Validate a token with the OAuth provider Spotify.
#     """
#     if 'oauth_token' not in session.keys():
#             return redirect(url_for('.authentification'))
        
#     spotify = OAuth2Session(client_id, token=session['oauth_token'])
#     current_user_id_url = 'https://api.spotify.com/v1/me'

#     results = spotify.get(f'{current_user_id_url}').json()
#     user_id = results['id']
#     print(user_id)
    
#     url_classify = f'https://api.spotify.com/v1/users/{user_id}/playlists'

#     headers = CaseInsensitiveDict()
#     headers["Accept"] = "application/json"
#     headers["Content-Type"] = "application/json"

#     body = {'name':f"{genre}",'description':'New playlist description','public':False}

#     resp = spotify.post(f'{url_classify}', data = json.dumps(body)).json()

#     playlist_id = resp['id']

#     uri_track = f'spotify:track:{track_id}'
#     url_post_track = "https://api.spotify.com/v1/playlists/{playlist_id}/tracks?position=1&uris={uri_track}"

#     resp = requests.post(url_post_track, headers=headers)

#     return {'answer':True}

    
