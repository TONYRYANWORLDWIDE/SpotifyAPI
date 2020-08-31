from flask import Flask,session, render_template, request, redirect, url_for, flash, jsonify
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
from getgenres import genreList
app = Flask(__name__)
app.secret_key = os.urandom(24)

sexytimeplaylistid=''
client_id = config.client_id
client_secret = config.client_secret
# redirect_uri = 'https://spotifysexytime.azurewebsites.net/callback'
redirect_uri = 'http://127.0.0.1:5000/callback' 
API_BASE = 'https://accounts.spotify.com'
scope = "playlist-modify-public playlist-modify-private user-modify-playback-state user-top-read"
scope += " user-modify-playback-state user-read-playback-state user-library-read user-library-modify"
SHOW_DIALOG = True
# CACHE = ".cache-" + "tonyryanworldwide"
CACHE = '.spotipyoauthcache'


@app.route('/')
def verify():
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = client_id, client_secret = client_secret, redirect_uri = redirect_uri, scope = scope,cache_path=CACHE)
    auth_url = sp_oauth.get_authorize_url()
    # print("auth url:" ,auth_url)
    return redirect(auth_url)

@app.route("/sexytime")
def index():
    return render_template("sexytime.html",sexytimeplaylistid=sexytimeplaylistid)

@app.route("/genres")
def genres():
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')   
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    gen = genreList()
    gen.sp = sp
    user =sp.current_user()['id']
    genres , finaltrackinfo = gen.getgenres()     
    return render_template('genres.html', genres=genres)


@app.route('/genrePlaylist',methods=['POST'])
def genrePlaylist():
    # session['token_info'], authorized = get_token(session)
    # session.modified = True
    # if not authorized:
    #     return redirect('/')   
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    gen = genreList()
    gen.sp = sp
    user =sp.current_user()['id']
    genres , finaltrackinfo = gen.getgenres()
    if request.method == 'POST':
        playlistlength = request.form['playlistlength']
        print("playlistlength{0}".format(playlistlength))
        if playlistlength == '':
            playlistlength = 600
            print("playlistlength none:{0}".format(playlistlength))
        playlistseconds = int(playlistlength) * 60
        # genrelist = request.form['genres']
        genrelist = request.form.getlist('genres')
        for g in genrelist:
            id = sp.user_playlist_create(user=user,name =g)['id']
            tracks = gen.genrefilter(finaltrackinfo,g,playlistseconds)
            # print(user,id,tracks)
            # sp.user_playlist_add_tracks(user = user, playlist_id =id,tracks = tracks,position = 0)
            lengthtracks = len(tracks)
            x= 0
            if lengthtracks <= 100:
                y = lengthtracks
                sp.user_playlist_add_tracks(user = user, playlist_id =id,tracks = tracks[x:y],position = 0)
            else:
                y = 100
                sp.user_playlist_add_tracks(user = user, playlist_id =id,tracks = tracks[x:y],position = 0)
                iteration = 1
                while y >0:
                    x = x +100
                    if lengthtracks < x  + 100:
                        y = lengthtracks   
                        sp.user_playlist_add_tracks(user = user, playlist_id =id,tracks = tracks[x:y],position = 0)
                        y = 0
                    else:
                        y = y + 100
                        sp.user_playlist_add_tracks(user = user, playlist_id =id,tracks = tracks[x:y],position = 0)
                    iteration += 1
        tracks = sp.playlist_tracks(id)['items']
    return render_template('playlist.html',tracks = tracks)


@app.route("/go" , methods=['POST'])
def create_sexytime_playlist():
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')   
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    if request.method == 'POST':
        studlength = request.form['studlength']
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
    token_info = sp_oauth.get_access_token(code,check_cache=False)#, -try this next if still broken
    # Saving the access token along with all other token related info
    session["token_info"] = token_info
    return redirect("index")

if __name__ == '__main__':  # ensure function only runs if executed from the python interpreter
    # app.secret_key = 'super_secret_key2'
    app.debug = True        # server will reload itself whenever a change is made
    app.run(host = '0.0.0.0' , port = 5000)