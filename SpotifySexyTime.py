#!/usr/bin/env python
# coding: utf-8


import os
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
import json

client_id = SPOTIPY_CLIENT_ID ='bb7c475418484e7784d9cd25b5f9f52c'
client_secret = SPOTIPY_CLIENT_SECRET='b0da0baeeab1499884912aea11f4ca58'
redirect_uri =SPOTIPY_REDIRECT_URI='https://localhost:8080/callback/'


os.environ["SPOTIPY_CLIENT_ID"] = "bb7c475418484e7784d9cd25b5f9f52c"
os.environ["SPOTIPY_CLIENT_SECRET"] = "b0da0baeeab1499884912aea11f4ca58"
os.environ["SPOTIPY_REDIRECT_URI"] = "https://localhost:8080/callback/"

scope = "playlist-modify-public playlist-modify-private user-modify-playback-state user-top-read"
username = 'tonyryanworldwide'

        
token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)        
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,username=username,))


playlists =sp.user_playlists(username)['items']
ijusthadsexid = '5PEleSkK4p4E1sx3x7cOLt'
ijusthadsexid_length = sp.track(ijusthadsexid)['duration_ms'] / 1000

studlength = input("How many minutes can you last: ")
studlength = int(studlength)
studlength_seconds = studlength * 60

for playlist in playlists:
    if playlist['name'] == 'sexy time':
        sexytimeplaylistid = playlist['uri']

sexytimetracks = sp.playlist_tracks(sexytimeplaylistid)['items']
sexytimetracks_ids = []

current_duration_seconds = ijusthadsexid_length
for track in sexytimetracks:
    current_duration_seconds += (track['track']['duration_ms'])/1000
    sexytimetracks_ids.append(track['track']['id'])

if current_duration_seconds < studlength_seconds:
    difference = studlength_seconds - current_duration_seconds
    print("add {0} more seconds".format(str(difference)))
    
toptracks = sp.current_user_top_tracks(limit=10)['items']
id = []
idlength = 0
while difference > 0:
    print (difference)
    for tracks in toptracks:   
        name = tracks['name']
        analysis = sp.audio_analysis(tracks['id'])
        tempo = analysis['track']['tempo']
        duration = tracks['duration_ms'] / 1000
        trackid = [tracks['id']]
        if (sexytimetracks_ids.count(tracks['id']) == 0):
            if tempo < 100:
                sp.user_playlist_add_tracks(user = username, playlist_id =sexytimeplaylistid,tracks = trackid,position = 0 )
                difference = difference - duration
                if difference < 0:
                    break  



