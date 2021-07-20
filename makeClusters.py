import pandas 
from getgenres import genreList
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import numpy as np
from sklearn.cluster import KMeans



class MakeClusters():
    def __init__(self):
        self.sp = ''
        self.numclustertest = 20       
       
    def getNumClusters(self,audio_features):
        numclustertest = self.numclustertest
        wcss = []
        for i in range(1, numclustertest):
            kmeans = KMeans(n_clusters = i)
            # Fit the Iris data points
            kmeans.fit(audio_features.values)
            # Get the WCSS (inertia) value
            wcss.append(kmeans.inertia_)
        for i in range(2,numclustertest):
            diflast = wcss[i-1] - wcss[i-2]
            dif = wcss[i] - wcss[i-1]
            if dif < diflast:
                n_clusters = i
                break
        return n_clusters

    def getAudioFeaturesAndLabels(self,tracks):
        sp = self.sp
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
        return audio_features,audio_labels

    def deleteExistingClusters(self):
        sp = self.sp
        user =sp.current_user()['id']        
        lenplaylists = 1
        offset = 0
        while lenplaylists > 0:
            playlists = sp.user_playlists(user,offset=offset)['items']
            lenplaylists = len(playlists)            
            for playlist in playlists:
                name= playlist['name'] 
                id = playlist['uri'][-22:]    
                if name[0:7] =='Cluster':
                    sp.user_playlist_unfollow(user=user, playlist_id = id)
            offset += 20

    def buildClassifierDict(self,audio_labels,km_clusters):
        classifier_dict = {}        
        for x in range(0,len(audio_labels)):
            classifier_dict[audio_labels[x]] = km_clusters[x] 
        return classifier_dict 

    def createClusterPlaylist(self,n_clusters,classifier_dict):
        sp = self.sp
        user =sp.current_user()['id'] 
        for cluster in range(0,n_clusters):
            name = 'Cluster Number ' + str(cluster)
            id = sp.user_playlist_create(user=user,name=name)['id']
            globals()[f"cluster_{cluster}"] = []
            for (key, value) in classifier_dict.items():
                if value == cluster:
                    globals()[f"cluster_{cluster}"].append(key)
            tracks = globals()[f"cluster_{cluster}"]
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
                    if lengthtracks <= x  + 100:
                        y = lengthtracks   
                        sp.user_playlist_add_tracks(user = user, playlist_id =id,tracks = tracks[x:y],position = 0)
                        y = 0
                    else:
                        y = y + 100
                        sp.user_playlist_add_tracks(user = user, playlist_id =id,tracks = tracks[x:y],position = 0)
                    iteration += 1

    def clusterize(self):
        sp = self.sp        
        user =sp.current_user()['id']
        gen = genreList()
        gen.sp = sp
        trackinfo = gen.getTrackInfo()
        tracks = list(trackinfo.keys())
        audio_features,audio_labels = self.getAudioFeaturesAndLabels(tracks)       
        # # Get two principal components
        pca = PCA(n_components=2).fit(audio_features.values)
        audio_2d = pca.transform(audio_features.values)
        audio_2d[0:10]
        n_clusters = self.getNumClusters(audio_features)
        model = KMeans(n_clusters=n_clusters, init='k-means++', n_init=50, max_iter=300,verbose= True,random_state = 56)
        # Fit to the iris data and predict the cluster assignments for each data point
        km_clusters = model.fit_predict(audio_features.values)        
        #Delete Existing Clusters
        self.deleteExistingClusters()
        classifier_dict = self.buildClassifierDict(audio_labels,km_clusters)
        self.createClusterPlaylist(n_clusters,classifier_dict)