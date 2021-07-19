import itertools
from itertools import combinations

def createplaylist(sp,studlength):
    user =sp.current_user()['id']
    playlists =sp.user_playlists(user)['items']
    sexytimeplaylistid = ''
    #Create sexytime playlist if it doesn't already exist
    for playlist in playlists:
        if playlist['name'] == 'sexy time':
            sexytimeplaylistid = playlist['uri']
    if sexytimeplaylistid == '':
        sexytimeplaylistid = sp.user_playlist_create(user=user, name ='sexy time',public = True,description = "Give it to her good")['id']
    #Get Potential tracks based on whats already in sexy time if it exists and users top tracks
    get_tracklengths(sp,studlength,sexytimeplaylistid,user)
    return sexytimeplaylistid
    
def get_tracklengths(sp,studlength,sexytimeplaylistid,user):
#     print("getracklengths")
    studlength_seconds = int(studlength) * 60
    sexytimetracks = sp.playlist_tracks(sexytimeplaylistid)['items']
    tracklength = {}
    toptracks = sp.current_user_top_tracks(limit=50)['items']
    # print("toptracks", toptracks)
    exclude_genres = ['east coast hip hop','movie tunes','folk punk','healing']
    for track in sexytimetracks:
        if track['track']['id'] != '5PEleSkK4p4E1sx3x7cOLt':
            tracklength[track['track']['id']] = track['track']['duration_ms'] / 1000
    for track2 in toptracks:
        if track2['id'] != '5PEleSkK4p4E1sx3x7cOLt':
            tracklength[track2['id']] = track2['duration_ms'] / 1000
    tracks=sp.tracks(tracklength.keys())
    
    tracks=sp.tracks(tracklength.keys())
    for trk in tracks['tracks']:
        id = trk['id']
        name = trk['name']
        artist = trk['artists'][0]['id']
        try:
            genre = sp.artist(artist)['genres'][0]
        except:
            genre = ''
        if (genre in exclude_genres): 
            del tracklength[id]

    features = sp.audio_features(tracklength.keys())
    for feature in features:
        id = feature['id']
        tempo = feature['tempo']
        if tempo > 100:
            del tracklength[id]   


    tracklengths = list(tracklength.values())
    sumtracklengh = sum(tracklengths) 
    totaltracks  = len(tracklengths)
    if totaltracks != 0:
        average_track_length = sumtracklengh / totaltracks
    else:
         average_track_length = 240

    numberofsongsneeded = round(studlength_seconds / average_track_length)
    print(sum(tracklength.values()))
    if numberofsongsneeded > len(tracklength):
        trackstoadd = list(tracklength.keys())
        deleteAndRepopulate(sp,trackstoadd,user,sexytimeplaylistid)
    else:
        result_shown = find_closest_sum(tracklength,studlength_seconds,numberofsongsneeded)
        trackstoadd = list(result_shown.keys())
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