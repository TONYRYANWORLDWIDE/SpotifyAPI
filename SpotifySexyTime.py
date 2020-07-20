#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
import itertools
from itertools import combinations


client_id = SPOTIPY_CLIENT_ID ='bb7c475418484e7784d9cd25b5f9f52c'
client_secret = SPOTIPY_CLIENT_SECRET='b0da0baeeab1499884912aea11f4ca58'
redirect_uri = 'https://localhost:8080/callback/'


# os.environ["SPOTIPY_CLIENT_ID"] = "bb7c475418484e7784d9cd25b5f9f52c"
# os.environ["SPOTIPY_CLIENT_SECRET"] = "b0da0baeeab1499884912aea11f4ca58"
# os.environ["SPOTIPY_REDIRECT_URI"] = "https://localhost:8080/callback/"

scope = "playlist-modify-public playlist-modify-private user-modify-playback-state user-top-read"
scope +=            " user-modify-playback-state user-read-playback-state user-library-read user-library-modify"
# username = '1238315340'
username ='tonyryanworldwide'

        
token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)        
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,username=username))


playlists =sp.user_playlists(username)['items']
ijusthadsexid = '5PEleSkK4p4E1sx3x7cOLt'
ijusthadsexid_length = sp.track(ijusthadsexid)['duration_ms'] / 1000

studlength = input("How many minutes can you last: ")
studlength = int(studlength)
studlength_seconds = studlength * 60
sexytimeplaylistid = ''
for playlist in playlists:
    if playlist['name'] == 'sexy time':
        sexytimeplaylistid = playlist['uri']

if sexytimeplaylistid == '':
    sexytimeplaylistid = sp.user_playlist_create(user=username, name ='sexy time',public = False,description = "Give it to her good")['id']
        


sexytimetracks = sp.playlist_tracks(sexytimeplaylistid)['items']
tracklength = {}
toptracks = sp.current_user_top_tracks(limit=50)['items']
for track in sexytimetracks:
    if track['track']['id'] != '5PEleSkK4p4E1sx3x7cOLt':
        tracklength[track['track']['id']] = track['track']['duration_ms'] / 1000
        
for track2 in toptracks:
    
    if track2['id'] != '5PEleSkK4p4E1sx3x7cOLt':
        tracklength[track2['id']] = track2['duration_ms'] / 1000
        
for tracks in tracklength.copy():
    analysis = sp.audio_analysis(tracks)
#     features = sp.audio_features(tracks)
    tempo = analysis['track']['tempo']
    if tempo > 100:
        del tracklength[tracks]


tracklengths = list(tracklength.values())
average_track_length = sum(tracklengths) / len(tracklengths)
numberofsongsneeded = round(studlength_seconds / average_track_length)

def find_closest_sum(numbers, target, n):
    permlist = list(map(dict, itertools.combinations(numbers.items(), n)))
    sumlist = [sum(l.values()) for l in permlist]    
    maxpos = 0
    for i in range(1, len(sumlist)):
        if abs(sumlist[i] - target) < abs(sumlist[maxpos]-target):
             maxpos = i
    return permlist[maxpos]

result_shown = find_closest_sum(tracklength, studlength_seconds, numberofsongsneeded)
trackstoadd = list(result_shown.keys())


sexytimetracks = sp.playlist_tracks(sexytimeplaylistid)['items']
deletelist = []
for x in sexytimetracks:
    deletelist.append(x['track']['id'])
    sp.user_playlist_remove_all_occurrences_of_tracks(username,sexytimeplaylistid,deletelist)   

sp.user_playlist_add_tracks(user = username, playlist_id =sexytimeplaylistid,tracks = [ijusthadsexid],position = 0 )
sp.user_playlist_add_tracks(user = username, playlist_id =sexytimeplaylistid,tracks = trackstoadd,position = 0 )

