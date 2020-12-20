import numpy as np
import os
import tensorflow as tf
import cv2
from scipy.sparse import csr_matrix
from sklearn import preprocessing
from sklearn.neighbors import NearestNeighbors

class SimilarityEngine():
    def __init__(self, model):
        self.model = model
    
    # def sortSimilarity(self, query, images):
    #     query_img_type_features,  query_img_type_labels = self.model(tf.convert_to_tensor(query[None, :]), training=False)
    #     given_img_type_features,  given_img_type_labels = self.model(tf.convert_to_tensor(images), training=False)
        
    #     # Converting the image features and labels to numpy and standardizing them
    #     query_img_type_features = query_img_type_features.numpy() #preprocessing.StandardScaler().fit_transform(query_img_type_features.numpy())
    #     query_img_type_labels = query_img_type_labels.numpy()
    #     given_img_type_features = given_img_type_features.numpy() #preprocessing.StandardScaler().fit_transform(given_img_type_features.numpy())
    #     given_img_type_labels = np.argmax(given_img_type_labels.numpy(), axis=1)
        
    #     itemLoc = np.argmax(query_img_type_labels)
    #     given_img_type_locs_top = np.where(given_img_type_labels == itemLoc)[0]
    #     given_img_type_features_top = given_img_type_features[given_img_type_labels == itemLoc]

    #     given_img_type_locs = np.where(given_img_type_labels != itemLoc)[0]
    #     given_img_type_features = given_img_type_features[given_img_type_labels != itemLoc]

    #     sorted_indices = []
    #     temp = []
    #     if len(given_img_type_features_top) > 0:
    #         N_N = NearestNeighbors(n_neighbors=len(given_img_type_features_top), algorithm= 'brute', metric= 'cosine').fit(given_img_type_features_top)
    #         distance, ind = N_N.kneighbors(query_img_type_features)
    #         sorted_indices += given_img_type_locs_top[ind[0]].tolist()
    #         temp = sorted_indices

    #     if len(given_img_type_features) > 0:
    #         N_N = NearestNeighbors(n_neighbors=len(given_img_type_features), algorithm= 'brute', metric= 'cosine').fit(given_img_type_features)
    #         distance, ind = N_N.kneighbors(query_img_type_features)
    #         sorted_indices += given_img_type_locs[ind[0]].tolist()
        
    #     return sorted_indices, temp
    
    def check(self):
        print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
        print("check")