import cv2
import numpy as np
import tensorflow as tf
import sys
import os
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
from django.conf import settings
config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)


class SegmentationEngine(object):
    def __init__(self, model):
        self.model = model
        
    def segment(self, img, h, w):
        img = tf.image.resize_with_pad(img,target_height=h,target_width=w)
        rgb  = img.numpy()
        fl = np.expand_dims(img,axis=0)/ 255.
        seq = self.model.predict(fl)
        seq = seq[3][0,:,:,0]
        seq = np.expand_dims(seq,axis=-1)
        c1x = rgb*seq
        c2x = rgb*(1-seq)
        cfx = c1x+c2x
        dummy = np.ones((rgb.shape[0],rgb.shape[1],1))
        rgbx = np.concatenate((rgb,dummy*255),axis=-1)
        rgbs = np.concatenate((cfx,seq*255.),axis=-1)
        return np.where(seq < 0.7, 255, c1x), rgbs




