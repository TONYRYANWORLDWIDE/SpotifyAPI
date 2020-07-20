import itertools
from itertools import combinations

def createplaylist(sp,studlength):
    print("createplaylist")
    user =sp.current_user()['id']
    playlists =sp.user_playlists(user)['items']
    sexytimeplaylistid = ''
    #Create sexytime playlist if it doesn't already exist
    for playlist in playlists:
        if playlist['name'] == 'sexy time':
            sexytimeplaylistid = playlist['uri']
    if sexytimeplaylistid == '':
        sexytimeplaylistid = sp.user_playlist_create(user=user, name ='sexy time',public = False,description = "Give it to her good")['id']
    #Get Potential tracks based on whats already in sexy time if it exists and users top tracks
    get_tracklengths(sp,studlength,sexytimeplaylistid,user)
    return sexytimeplaylistid
    
def get_tracklengths(sp,studlength,sexytimeplaylistid,user):
    print("getracklengths")
    studlength_seconds = int(studlength) * 60
    sexytimetracks = sp.playlist_tracks(sexytimeplaylistid)['items']
    tracklength = {}
    toptracks = sp.current_user_top_tracks(limit=50)['items']
    # print("toptracks", toptracks)

    for track in sexytimetracks:
        if track['track']['id'] != '5PEleSkK4p4E1sx3x7cOLt':
            tracklength[track['track']['id']] = track['track']['duration_ms'] / 1000
    for track2 in toptracks:
        if track2['id'] != '5PEleSkK4p4E1sx3x7cOLt':
            tracklength[track2['id']] = track2['duration_ms'] / 1000
    for tracks in tracklength.copy():
        analysis = sp.audio_analysis(tracks)
        tempo = analysis['track']['tempo']
        if tempo > 100:
            del tracklength[tracks]
    tracklengths = list(tracklength.values())
    sumtracklengh = sum(tracklengths) 
    totaltracks  = len(tracklengths)
    if totaltracks != 0:
        average_track_length = sumtracklengh / totaltracks
    else:
         average_track_length = 240
    print(sumtracklengh, totaltracks, average_track_length,studlength_seconds)
    # average_track_length = sum(tracklengths) / len(tracklengths)
    numberofsongsneeded = round(studlength_seconds / average_track_length)
    result_shown = find_closest_sum(tracklength,studlength_seconds,numberofsongsneeded)
    trackstoadd = list(result_shown.keys())
    print("tracks to add")
    deleteAndRepopulate(sp,trackstoadd,user,sexytimeplaylistid)
    
def find_closest_sum(numbers, target, n):
    permlist = list(map(dict, itertools.combinations(numbers.items(), n)))
    sumlist = [sum(l.values()) for l in permlist]    
    maxpos = 0
    for i in range(1, len(sumlist)):
        if abs(sumlist[i] - target) < abs(sumlist[maxpos]-target):
             maxpos = i
    return permlist[maxpos]

def deleteAndRepopulate(sp,trackstoadd,user,sexytimeplaylistid):
    ijusthadsexid = '5PEleSkK4p4E1sx3x7cOLt'
    sexytimetracks = sp.playlist_tracks(sexytimeplaylistid)['items']
    deletelist = []
    for x in sexytimetracks:
        deletelist.append(x['track']['id'])
        sp.user_playlist_remove_all_occurrences_of_tracks(user,sexytimeplaylistid,deletelist)
    sp.user_playlist_add_tracks(user = user, playlist_id =sexytimeplaylistid,tracks = [ijusthadsexid],position = 0 )
    sp.user_playlist_add_tracks(user = user, playlist_id =sexytimeplaylistid,tracks = trackstoadd,position = 0 )