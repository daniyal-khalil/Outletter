import numpy as np
import os
import tensorflow as tf
import cv2
from scipy.sparse import csr_matrix
from sklearn import preprocessing
from sklearn.neighbors import NearestNeighbors
from tensorflow.keras.models import load_model
import time
from src.choices import LabelChoicesQueried as lc

class SimilarityEngine():
	def __init__(self, model):
		self.model = model
		self.labels = [lc.SHORT_SLEEVED_SHIRT, lc.LONG_SLEEVED_SHIRT, lc.SHORT_SLEEVED_OUTWEAR, lc.LONG_SLEEVED_OUTWEAR,
				lc.VEST, lc.SLING, lc.SHORTS, lc.TROUSERS, lc.SKIRT, lc.SHORT_SLEEVED_DRESS, lc.LONG_SLEEVED_DRESS,
				lc.VEST_DRESS, lc.SLING_DRESS, lc.NONE]
	
	def predict_image(self, images):
		images = np.array(images)
		if images.ndim == 3:
			query_img_type_features,  query_img_type_labels = self.model(images[None, :], training=False)
			itemLoc = np.argmax(query_img_type_labels)
			return query_img_type_features, itemLoc
		elif images.ndim == 4:
			return self.model(images, training=False)
		
	def decode_query_label(self, itemLoc):
		return self.labels[itemLoc]

	def sortSimilarity(self, query_image_type_label, query_img_type_features, given_img_type_features, given_img_type_labels):
		it = time.time()
		# Converting the image features and labels to numpy and standardizing them
		query_img_type_features = query_img_type_features.numpy() #preprocessing.StandardScaler().fit_transform(query_img_type_features.numpy())

		given_img_type_features = given_img_type_features.numpy() #preprocessing.StandardScaler().fit_transform(given_img_type_features.numpy())
		given_img_type_labels = np.argmax(given_img_type_labels.numpy(), axis=1)
		
		itemLoc = self.labels.index(query_image_type_label)

		given_img_type_locs_top = np.where(given_img_type_labels == itemLoc)[0]
		given_img_type_features_top = given_img_type_features[given_img_type_labels == itemLoc]
		given_img_type_labels_top = given_img_type_labels[given_img_type_labels == itemLoc]

		given_img_type_locs = np.where(given_img_type_labels != itemLoc)[0]
		given_img_type_features = given_img_type_features[given_img_type_labels != itemLoc]
		given_img_type_labels = given_img_type_labels[given_img_type_labels != itemLoc]

		sorted_indices = []
		sorted_labels = []
		if len(given_img_type_features_top) > 0:
			N_N = NearestNeighbors(n_neighbors=len(given_img_type_features_top), algorithm= 'brute', metric= 'cosine').fit(given_img_type_features_top)
			distance, ind = N_N.kneighbors(query_img_type_features)
			sorted_indices += given_img_type_locs_top[ind[0]].tolist()
			sorted_labels += [self.labels[t] for t in given_img_type_labels_top[ind[0]]]

		if len(given_img_type_features) > 0:
			N_N = NearestNeighbors(n_neighbors=len(given_img_type_features), algorithm= 'brute', metric= 'cosine').fit(given_img_type_features)
			distance, ind = N_N.kneighbors(query_img_type_features)
			sorted_indices += given_img_type_locs[ind[0]].tolist()
			sorted_labels += [self.labels[t] for t in given_img_type_labels[ind[0]]]
		
		ft = time.time()
		print("sim TIme: " + str(ft - it))

		return sorted_indices, sorted_labels