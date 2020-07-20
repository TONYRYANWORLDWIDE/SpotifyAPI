from flask import Flask,session, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)
import os
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
import itertools
from itertools import combinations
import datetime
import json
import urllib
import config
import requests
import time
from createplaylist import createplaylist

sexytimeplaylistid=''
client_id = config.client_id
client_secret = config.client_secret
redirect_uri = 'http://127.0.0.1:5000/callback'
API_BASE = 'https://accounts.spotify.com'
scope = "playlist-modify-public playlist-modify-private user-modify-playback-state user-top-read"
scope += " user-modify-playback-state user-read-playback-state user-library-read user-library-modify"
SHOW_DIALOG = True
CACHE = ".cache-" + "tonyryanworldwide"


@app.route('/')
def verify():
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = client_id, client_secret = client_secret, redirect_uri = redirect_uri, scope = scope,cache_path=CACHE)
    auth_url = sp_oauth.get_authorize_url()
    # print("auth url:" ,auth_url)
    return redirect(auth_url)

@app.route("/index")
def index():
    return render_template("index.html",sexytimeplaylistid=sexytimeplaylistid)


@app.route("/go" , methods=['POST'])
def create_sexytime_playlist():
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')   
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    if request.method == 'POST':
        studlength = request.form['studlength']

        print("creatinglist")
        sexytimeplaylistid = createplaylist(sp,studlength)
        tracks = sp.playlist_tracks(sexytimeplaylistid)['items']
                 
    return render_template("playlist.html",sexytimeplaylistid=sexytimeplaylistid,tracks=tracks)

def get_token(session):
    token_valid = False
    token_info = session.get("token_info", {})
    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid
    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60
    # Refreshing token if it has expired
    if (is_token_expired):
        # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = CLI_ID, client_secret = CLI_SEC, redirect_uri = REDIRECT_URI, scope = SCOPE,cache_path=CACHE)
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))
    token_valid = True
    return token_info, token_valid

@app.route("/callback")
def callback():
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = client_id, client_secret = client_secret, redirect_uri = redirect_uri, scope = scope,cache_path=CACHE)
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    # Saving the access token along with all other token related info
    session["token_info"] = token_info
    return redirect("index")

if __name__ == '__main__':  # ensure function only runs if executed from the python interpreter
    app.secret_key = 'super_secret_key2'
    app.debug = True        # server will reload itself whenever a change is made
    app.run(host = '0.0.0.0' , port = 5000)