import pandas 
from getgenres import genreList
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import numpy as np
from sklearn.cluster import KMeans
import itertools
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure



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

    def plot_clusters(self,samples,clusters,n_clusters):
        col_dic_base = {0:'blue',1:'green',2:'orange',3:'red',4:'yellow',
                5:'black',6:'teal',7: 'brown', 8: 'purple',9: 'azure',
                10:'slateblue',11:'green',12:'indianred',13:'orange',14:'yellow',
                15:'black',16:'teal',17: 'brown', 18: 'purple',19: 'azure',
               20:'thistle',21:'lightcyan'}
        mrk_dic_base = {0:'*',1:'x',2:'+',3:'p',4:'h',
                5:'d',6:'<',7:'>',8:'*',9:'v',
                10:'o',11:'.',12:'^',13:'s',14:'$&$',
                15:'$@$',16:'$G$',17:'$4$',18:'$?$',19:'$19$',
               20:'$P$',21:'$H$'}
        col_dic = dict(itertools.islice(col_dic_base.items(), n_clusters))
        mrk_dic = dict(itertools.islice(mrk_dic_base.items(), n_clusters))
        colors = [col_dic[x] for x in clusters]
        markers = [mrk_dic[x] for x in clusters]
        for sample in range(len(clusters)):
            plt.scatter(samples[sample][0], samples[sample][1], color = colors[sample], marker=markers[sample], s=100)
            plt.xlabel('Dimension 1')
            plt.ylabel('Dimension 2')
            plt.title('Assignments')   
            # path not recognized TODO 
            # plt.savefig('/static/images/featuresplot.png')
            # plt.savefig('featuresplot.png')

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
        self.plot_clusters(audio_2d,km_clusters,n_clusters)
