import pandas as pd
from pandas import DataFrame



class makeplaylistFromTrack():

    def __init__(self):
        self.sp = ''
    
    def getsavedsongs(self):
        sp = self.sp
        currentsong = sp.current_playback()
        if currentsong is None:
            print('Nothing''s playing homie')
            playlistname = 'No Playlists'
            playlistimage = ''
            return playlistname,playlistimage
        currenturi = currentsong['item']['external_urls']['spotify']
        currentsongid = currentsong['item']['id']
        progress_ms = currentsong['progress_ms']
        user =sp.current_user()['id']
        playlists = sp.user_playlists(user,offset=0)['items']
        playlistbase = (sp.user_playlists(user,offset=50)['items'])
        for pl in playlistbase:
            playlists.append(pl)
        playlistids =[]
        for playlist in playlists:
            playlistid = playlist['id']
            playlistname = playlist['name']
            playlistimage = playlist['images'][0]['url']
            context_uri = playlist['external_urls']['spotify']
            playlistids.append(playlistid)
            playlist_tracks = sp.playlist_tracks(playlistid)['items']
            for i in range(0,len(playlist_tracks)):
                trackid = playlist_tracks[i]['track']['id']            
                if (trackid == currentsongid):
                    print(trackid)
                    # if playlistname not in ignorelist:
                    print("trackid: {0} context_uri: {1} playlistname: {2} playlistid: {3}".format(trackid,context_uri,playlistname,playlistid))
                    sp.start_playback(context_uri = context_uri,offset ={'position':i},position_ms=progress_ms)
                    print(playlistimage)
                    return playlistname,playlistimage# "trackid: {0} context_uri: {1} playlistname: {2} playlistid: {3}".format(trackid,context_uri,playlistname,playlistid)             
        print('No Playlists')
        playlistname = 'No Playlists'
        playlistimage = ''
        return playlistname,playlistimage#'No Playlists'
