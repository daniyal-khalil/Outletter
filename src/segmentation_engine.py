import cv2
import numpy as np
import torch
import time
from src.choices import LabelChoicesQueried as lc

class SegmentationEngine(object):
    def __init__(self, model):
        self.model = model
        self.labels = [lc.SHORT_SLEEVED_SHIRT, lc.LONG_SLEEVED_SHIRT, lc.SHORT_SLEEVED_OUTWEAR, lc.LONG_SLEEVED_OUTWEAR,
                        lc.VEST, lc.SLING, lc.SHORTS, lc.TROUSERS, lc.SKIRT, lc.SHORT_SLEEVED_DRESS, lc.LONG_SLEEVED_DRESS,
                        lc.VEST_DRESS, lc.SLING_DRESS, lc.NONE]
    
    def aspect_resize(self, src, tar_h, tar_w):
        h,w,c = src.shape
        max_dim = max(h,w)
        if max_dim == h:
            max_dim_name = 'h'
        else:
            max_dim_name = 'w'
        if max_dim_name == 'h':
            ratio = tar_h / h
        else:
            ratio = tar_w / w

        new_h = (int)(round(ratio * h))
        new_w = (int)(round(ratio * w))
        src = cv2.resize(src, (new_w, new_h))

        if max_dim_name == 'h':
            diff = (int)((tar_w - new_w) / 2)
            dest = cv2.copyMakeBorder(src, 0, 0, diff, tar_w - new_w - diff, cv2.BORDER_CONSTANT, 255)
        else:
            diff = (int)((tar_h - new_h) / 2)
            dest = cv2.copyMakeBorder(src, diff, tar_h - new_h - diff, 0, 0, cv2.BORDER_CONSTANT, 255)

        return dest
    
    def cut_sides(self, img, img_mask):
        img_mask = img_mask.numpy()
        mask_sum_0 = np.sum(img_mask, axis=0)
        mask_sum_1 = np.sum(img_mask, axis=1)
        sum_0_l = np.where(mask_sum_0 != 0)[0][0]
        sum_0_r = np.where(mask_sum_0 != 0)[0][-1] + 1
        sum_1_t = np.where(mask_sum_1 != 0)[0][0]
        sum_1_b = np.where(mask_sum_1 != 0)[0][-1] + 1
        return img[sum_0_l:sum_0_r, sum_1_t:sum_1_b], img_mask[sum_0_l:sum_0_r, sum_1_t:sum_1_b]

    def apply_mask(self, img, output):
            instances = output["instances"].get_fields()
            image_instances = len(instances['pred_classes'])
            if image_instances == 0:
                return img, self.labels[13], img
            else:
                img_scores = instances['scores'].cpu()
                loc = np.argmax(img_scores)
                img_mask = instances['pred_masks'][loc].cpu()
                img, img_mask = self.cut_sides(img, img_mask)
                alpha_img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
                alpha_img[:, :, 3] = img_mask  * 255
                img = np.where(np.stack((img_mask,)*3, axis=-1) , img, 255)
                return img, self.labels[instances['pred_classes'][loc]], alpha_img
    
    def segment(self, imgs, h, w):
        it = time.time()
        imgs = [self.aspect_resize(img, 800, 800) for img in imgs]
        input_imgs = [{"image": torch.from_numpy(img.transpose((2,0,1)))} for img in imgs]
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(input_imgs)
        seg_imgs = []
        for i in range(len(imgs)):
            image, label, png = self.apply_mask(imgs[i], outputs[i])
            if label != lc.NONE:
                seg_imgs.append((self.aspect_resize(image, h, w), label, self.aspect_resize(png, h, w)))
        ft = time.time()
        print("seg TIme: ", ft - it)
        return seg_imgs




