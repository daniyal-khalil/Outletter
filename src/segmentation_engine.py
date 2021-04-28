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
        #img_mask = img_mask.numpy()
        mask_sum_0 = np.sum(img_mask, axis=1)
        mask_sum_1 = np.sum(img_mask, axis=0)
        sum_0_l = np.where(mask_sum_0 != 0)[0][0]
        sum_0_r = np.where(mask_sum_0 != 0)[0][-1] + 1
        sum_1_t = np.where(mask_sum_1 != 0)[0][0]
        sum_1_b = np.where(mask_sum_1 != 0)[0][-1] + 1
        my_img = img[sum_0_l:sum_0_r, sum_1_t:sum_1_b]
        my_mask = img_mask[sum_0_l:sum_0_r, sum_1_t:sum_1_b]
        return my_img, my_mask

    def apply_mask(self, img, output, prev_label=lc.NONE):
            instances = output["instances"].get_fields()
            image_instances = len(instances['pred_classes'])
            if image_instances == 0:
                return img, self.labels[13], img
            else:
                img_scores = instances['scores'].cpu()
                img_labels = [self.labels[label] for label in instances['pred_classes'].cpu()]
                try:
                    loc = img_labels.index(prev_label)
                except:
                    loc = np.argmax(img_scores)
                img_mask = instances['pred_masks'][loc].cpu()
                img, img_mask = self.cut_sides(img, img_mask.numpy())
                alpha_img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
                alpha_img[:, :, 3] = img_mask  * 255
                img = np.where(np.stack((img_mask,)*3, axis=-1) , img, 255)
                return img, self.labels[instances['pred_classes'][loc]], alpha_img
    
    def segment(self, imgs, h, w, query=False, prev_label=lc.NONE):
        it = time.time()
        if query:
            imgs = self.aspect_resize(imgs, 800, 800)
            input_img = [{"image": torch.from_numpy(imgs.transpose((2,0,1)))}]
            self.model.eval()
            with torch.no_grad():
                output = self.model(input_img)[0]
            instances = output["instances"].get_fields()
            image_instances = len(instances['pred_classes'])
            if image_instances == 0:
                ft = time.time()
                print("No instance - seg TIme: ", ft - it)
                raise('No instance found!')
            else:
                seg_items = []
                for i in range(image_instances):
                    pred_mask = instances['pred_masks'][i].cpu()
                    pred_label = self.labels[instances['pred_classes'][i]]
                    img = np.copy(imgs)
                    alpha_img_trans = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
                    alpha_img_trans[:, :, 3] = (pred_mask  * 210) + 45
                    img, pred_mask = self.cut_sides(img, pred_mask.numpy())
                    alpha_img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
                    alpha_img[:, :, 3] = pred_mask  * 255
                    img = np.where(np.stack((pred_mask,)*3, axis=-1) , img, 255)
                    seg_items.append((self.aspect_resize(img,h,w), pred_label, alpha_img, alpha_img_trans))
                ft = time.time()
                print("seg TIme: ", ft - it)
                return seg_items
        else:
            imgs = [self.aspect_resize(img, 800, 800) for img in imgs]
            input_imgs = [{"image": torch.from_numpy(img.transpose((2,0,1)))} for img in imgs]
            self.model.eval()
            with torch.no_grad():
                outputs = self.model(input_imgs)
            seg_imgs = []
            for i in range(len(imgs)):
                image, label, png = self.apply_mask(imgs[i], outputs[i], prev_label=prev_label)
                if label != lc.NONE:
                    seg_imgs.append((self.aspect_resize(image, h, w), label, self.aspect_resize(png, h, w)))
            ft = time.time()
            print("seg TIme: ", ft - it)
            return seg_imgs




