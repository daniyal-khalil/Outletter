import numpy as np
import os
import tensorflow as tf
import cv2
from scipy.sparse import csr_matrix
from sklearn import preprocessing
from sklearn.neighbors import NearestNeighbors
from tensorflow.keras.models import load_model

class SimilarityEngine():
	def __init__(self, model):
		self.model = model
		self.labels = ["Bra", "Briefs", "Capris", "Casual Shoes", "Dresses", "Flats", "Flip Flops", "Formal Shoes", "Heels", "Innerwear Vests", "Jackets", "Jeans", "Kurtas", "Kurtis", "Leggings", "Night suits", "Nightdress", "Sandals", "Sarees", "Shirts", "Shorts", "Skirts", "Sports Shoes", "Sweaters", "Sweatshirts", "Tops", "Track Pants", "Trousers", "Trunk", "Tshirts", "Tunics"]
		
	def predict_image(self, img):
		# label = self.model(tf.convert_to_tensor(image[None, :]), training=False)
		# itemLoc = np.argmax(label)
		# return self.labels[itemLoc]
		print(img.shape)
		print(img[None, :].shape)
		# tf.convert_to_tensor()
		# query_img_type_features,  query_img_type_labels = self.model(img[None, :], training=False)
		# itemLoc = np.argmax(query_img_type_labels)
		# return query_img_type_features, itemLoc
		return 'ede', 'ded'
		
	def decode_query_label(self, itemLoc):
		return self.labels[itemLoc]

	def sortSimilarity(self, query_img_type_features,  itemLoc, images):
		# model = tf.keras.Model(inputs=self.model.layers[0].input,outputs=[self.model.layers[-2].output, self.model.layers[-1].output])
		# query_img_type_features,  query_img_type_labels = model(tf.convert_to_tensor(query[None, :]), training=False)
		given_img_type_features,  given_img_type_labels = self.model(tf.convert_to_tensor(images), training=False)
		
		# Converting the image features and labels to numpy and standardizing them
		query_img_type_features = query_img_type_features.numpy() #preprocessing.StandardScaler().fit_transform(query_img_type_features.numpy())
		# query_img_type_labels = query_img_type_labels.numpy()
		given_img_type_features = given_img_type_features.numpy() #preprocessing.StandardScaler().fit_transform(given_img_type_features.numpy())
		given_img_type_labels = np.argmax(given_img_type_labels.numpy(), axis=1)
		
		# itemLoc = np.argmax(query_img_type_labels)
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
		
		return sorted_indices, sorted_labels, self.labels[itemLoc]