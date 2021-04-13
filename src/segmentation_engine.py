import cv2
import numpy as np

class SegmentationEngine(object):
    def __init__(self, model):
        self.model = model
        self.labels = labels = ["short_sleeved_shirt", "long_sleeved_shirt", "short_sleeved_outwear", "long_sleeved_outwear", "vest", "sling", "shorts", "trousers",
          "skirt", "short_sleeved_dress", "long_sleeved_dress", "vest_dress", "sling_dress"]
    
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
            dest = cv2.copyMakeBorder(src, 0, 0, diff, tar_w - new_w - diff, cv2.BORDER_CONSTANT, 0)
        else:
            diff = (int)((tar_h - new_h) / 2)
            dest = cv2.copyMakeBorder(src, diff, tar_h - new_h - diff, 0, 0, cv2.BORDER_CONSTANT, 0)

        return dest

    def apply_masks(self, images, outputs):
        output_images = []
        output_labels = []
        output_pngs = []
        for i in range(len(images)):
            img = images[i]
            instances = outputs[i]["instances"].get_fields()
            image_instances = len(instances['pred_classes'])
            if image_instances == 0:
                output_images.append(img)
                output_pngs.append(img)
                output_labels.append("None")
            else:
                img_scores = instances['scores']
                loc = np.argmax(img_scores)
                img_mask = instances['pred_masks'][loc]
                alpha_img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
                alpha_img[:, :, 3] = img_mask  * 255
                output_pngs.append(alpha_img)
                img = np.where(np.stack((img_mask,)*3, axis=-1) , img, 255)
                output_images.append(img)
                output_labels.append(self.labels[instances['pred_classes'][loc]])
        return output_images, output_labels, output_pngs
    
    def segment(self, imgs, h, w):
        output_images, output_labels, output_pngs = [], [], []
        for img in imgs:
            resized_img = self.aspect_resize(img, h, w)
            out_img, out_label, out_png = self.apply_masks([resized_img], [self.model(resized_img)])
            output_images.append(out_img[0])
            output_labels.append(out_label[0])
            output_pngs.append(out_png[0])
        return output_images, output_labels, output_pngs




