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
    def __init__(self, model, version=1.1):
        self.model   = model
        self.version = version
        
    def get_dress(self, imageid, stack=False):
        """limited to top wear and full body dresses (wild and studio working)"""
        """takes input rgb----> return PNG"""
        name =  imageid
        file = cv2.imread(name)
        file = tf.image.resize_with_pad(file,target_height=224,target_width=224)
        rgb  = file.numpy()
        file = np.expand_dims(file,axis=0)/ 255.
        seq = self.model.predict(file)
        seq = seq[3][0,:,:,0]
        seq = np.expand_dims(seq,axis=-1)
        c1x = rgb*seq
        c2x = rgb*(1-seq)
        cfx = c1x+c2x
        dummy = np.ones((rgb.shape[0],rgb.shape[1],1))
        rgbx = np.concatenate((rgb,dummy*255),axis=-1)
        rgbs = np.concatenate((cfx,seq*255.),axis=-1)
        if stack:
            stacked = np.hstack((rgbx,rgbs))
            return stacked
        else:
            return rgbs
        
        





