import pandas 
from getgenres import genreList
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import numpy as np
from sklearn.cluster import KMeans



class MakeClusters():
    def __init__(self):
        self.sp = ''       
       

    def clusterize(self):
        sp = self.sp
        user =sp.current_user()['id']

        gen = genreList()
        gen.sp = sp
        trackinfo = gen.getTrackInfo()
        tracks = list(trackinfo.keys())
        j = 0
        audfeat = []
        while j < len(tracks):
            audfeat = audfeat +  sp.audio_features(tracks[j:j+100])
            j += 100
        dfAudio = pandas.DataFrame(audfeat)
        dfAudio.drop(columns=['key','mode','type','uri','track_href','analysis_url'],inplace = True)
        audio_features = dfAudio[dfAudio.columns[0:8]]
        audio_labels = dfAudio['id'].values
        # Normalize the numeric features so they're on the same scale
        audio_features[dfAudio.columns[0:8]] = MinMaxScaler().fit_transform(audio_features[dfAudio.columns[0:8]])
        # # Get two principal components
        pca = PCA(n_components=2).fit(audio_features.values)
        audio_2d = pca.transform(audio_features.values)
        audio_2d[0:10]
        wcss = []
        for i in range(1, 50):
            kmeans = KMeans(n_clusters = i)
            # Fit the Iris data points
            kmeans.fit(audio_features.values)
            # Get the WCSS (inertia) value
            wcss.append(kmeans.inertia_)
        for i in range(2,len(wcss)):
            diflast = wcss[i-1] - wcss[i-2]
            dif = wcss[i] - wcss[i-1]
            if dif < diflast:
                n_clusters = i
                break
        model = KMeans(n_clusters=n_clusters, init='k-means++', n_init=50, max_iter=300,verbose= True,random_state = 56)
        # Fit to the iris data and predict the cluster assignments for each data point
        km_clusters = model.fit_predict(audio_features.values)
        
        #Delete Existing Clusters
        lenplaylists = 1
        offset = 0
        while lenplaylists > 0:
            playlists = sp.user_playlists(user,offset=offset)['items']
            lenplaylists = len(playlists)
            
            for playlist in playlists:
                name= playlist['name'] 
                id = playlist['uri'][-22:]    
                if name[0:7] =='Cluster':
                    # print('deleting{0} id {1}'.format(name,id))
                    sp.user_playlist_unfollow(user=user, playlist_id = id)
            offset += 20
        
        classifyer_dict = {}        
        for x in range(0,len(audio_labels)):
            classifyer_dict[audio_labels[x]] = km_clusters[x]
        
        
        for cluster in range(0,n_clusters):
            name = 'Cluster Number ' + str(cluster)
            id = sp.user_playlist_create(user=user,name=name)['id']
            globals()[f"cluster_{cluster}"] = []
            for (key, value) in classifyer_dict.items():
                if value == cluster:
                    globals()[f"cluster_{cluster}"].append(key)
            tracks = globals()[f"cluster_{cluster}"]
            lengthtracks = len(tracks)
            x= 0
            if lengthtracks <= 100:
                y = lengthtracks
                # print("x:{0} y:{1}".format(x,y))
                sp.user_playlist_add_tracks(user = user, playlist_id =id,tracks = tracks[x:y],position = 0)
            else:
                y = 100
                # print("1st else: x{} y{}".format(x,y))
                sp.user_playlist_add_tracks(user = user, playlist_id =id,tracks = tracks[x:y],position = 0)
                iteration = 1
                while y >0:
                    x = x +100
                    # print(x,lengthtracks, 'Length of x and tracks')
                    if lengthtracks <= x  + 100:
                        y = lengthtracks   
                        # print("inif: x{} y{}".format(x,y))
                        sp.user_playlist_add_tracks(user = user, playlist_id =id,tracks = tracks[x:y],position = 0)
                        y = 0
                    else:
                        y = y + 100
                        # print("else x:{} y:{}".format(x,y))
                        sp.user_playlist_add_tracks(user = user, playlist_id =id,tracks = tracks[x:y],position = 0)
                    iteration += 1

        
