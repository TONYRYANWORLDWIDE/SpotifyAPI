import pandas as pd
from pandas import DataFrame



class genreList():

    def __init__(self):
        self.sp = ''
    
    def getsavedsongs(self):
        sp = self.sp
        total = sp.current_user_saved_tracks()['total']
        offset = 50
        savedtracks = sp.current_user_saved_tracks(limit = 50)['items']
        while offset < total:    
            savedtracks2 =sp.current_user_saved_tracks(limit = 50,offset=offset)['items']
            for track in savedtracks2:
                savedtracks.append(track)
            offset += 50    
        trackinfo ={}   
        for trackex in savedtracks:
            id = trackex['track']['id']
            name = trackex['track']['name']
            artistid = trackex['track']['artists'][0]['id']
            seconds = trackex['track']['duration_ms']/1000
            trackinfo[trackex['track']['id']] = {"artist" : artistid,"name":name,"seconds":seconds}

        self.trackdf = pd.DataFrame.from_dict(trackinfo,orient = "index").reset_index()
        self.trackdf.columns = ['trackid','artistid','trackname','tracklength_sec']
        return self.trackdf
    
    def getartists(self):
        sp = self.sp
        trackdf = self.getsavedsongs()
        artists = trackdf.artistid.unique()
        artistinfo = []
        i = 0
        while i < len(artists) - 50:
            x=sp.artists(artists[i:i+50])['artists']
            artistinfo.append(x)
            i+=50
        artistfinal ={}
        for i in artistinfo:
            for j in i:   
                id = j['id']
                name = j['name']
                if len(j['genres']) > 0:
                    genre = j['genres']#[0]
                else:
                    genre = ''
                artistfinal[id] = {"name":name,"genre": genre}          
        artistdf = pd.DataFrame.from_dict(artistfinal,orient = "index").reset_index()
        artistdf = artistdf.reset_index()[['index','name','genre']]
        artistdf.columns = ['artistid','artistname','genre']
        self.artistdf=artistdf[artistdf['genre']!=''].reset_index()[['artistid','artistname','genre']]
        return self.artistdf

    def getfinaltrackinfo(self):
        sp = self.sp
        artistdf = self.getartists()
        trackdf = self.trackdf
        column_names = ["artistid", "artistname", "genre"]
        finalartist = pd.DataFrame(columns = column_names)
        for i in range(0, len(artistdf)):
            df = artistdf[i:i+1][['artistid','artistname']]
            genres = artistdf[i:i+1]['genre'][i]
            gf= DataFrame(genres,columns=['genre'])
            product = (
            df.assign(key=1)
            .merge(gf.assign(key=1), on="key")
            .drop("key", axis=1)
            )
            finalartist = finalartist.append(product)
        self.finaltrackinfo = trackdf.merge(finalartist, left_on = 'artistid', right_on = 'artistid', how = 'inner' )
        self.finaltrackinfo['cum_sec'] = self.finaltrackinfo.groupby('genre')['tracklength_sec'].apply(lambda x: x.cumsum())
        return self.finaltrackinfo
    
    def getgenres(self):
        sp = self.sp
        finaltrackinfo = self.getfinaltrackinfo()
        genres = finaltrackinfo.groupby('genre').count().reset_index()[['genre','artistid']]
        genres.columns=['genre','count']
        genres = genres[(genres['count'] >= 25) & (genres['genre']!= '')].sort_values(by ='count', ascending = False)
        self.genrelist = genres['genre'].tolist()
        self.finaltrackinfo = finaltrackinfo[finaltrackinfo['genre'].isin(genres['genre'])]
        return self.genrelist, self.finaltrackinfo
        
    def genrefilter(self,df,gen,sec_lim = 36000):
        dfin = df['trackid'][(df['genre'] == gen) & (df['cum_sec'] <= sec_lim)]
        return dfin.tolist()#[0:100]