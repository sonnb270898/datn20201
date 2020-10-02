"""  
Copyright (c) 2019-present NAVER Corp.
MIT License
"""

# -*- coding: utf-8 -*-
import numpy as np
# from skimage import io
import cv2

def loadImage(img_file):
    img = cv2.imread(img_file,cv2.COLOR_BGR2RGB)           # RGB order
    if img.shape[0] == 2: img = img[0]
    if len(img.shape) == 2 : img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if img.shape[2] == 4:   img = img[:,:,:3]

    return img

def normalizeMeanVariance(in_img, mean=(0.485, 0.456, 0.406), variance=(0.229, 0.224, 0.225)):
    # should be RGB order
    img = in_img.copy().astype(np.float32)

    img -= np.array([mean[0] * 255.0, mean[1] * 255.0, mean[2] * 255.0], dtype=np.float32)
    img /= np.array([variance[0] * 255.0, variance[1] * 255.0, variance[2] * 255.0], dtype=np.float32)
    return img

def denormalizeMeanVariance(in_img, mean=(0.485, 0.456, 0.406), variance=(0.229, 0.224, 0.225)):
    # should be RGB order
    img = in_img.copy()
    img *= variance
    img += mean
    img *= 255.0
    img = np.clip(img, 0, 255).astype(np.uint8)
    return img

def resize_aspect_ratio(img, square_size, interpolation, mag_ratio=1):
    height, width, channel = img.shape

    # magnify image size
    target_size = mag_ratio * max(height, width)

    # set original image size
    if target_size > square_size:
        target_size = square_size
    
    ratio = target_size / max(height, width)    

    target_h, target_w = int(height * ratio), int(width * ratio)
    proc = cv2.resize(img, (target_w, target_h), interpolation = interpolation)


    # make canvas and paste image
    target_h32, target_w32 = target_h, target_w
    if target_h % 32 != 0:
        target_h32 = target_h + (32 - target_h % 32)
    if target_w % 32 != 0:
        target_w32 = target_w + (32 - target_w % 32)
    resized = np.zeros((target_h32, target_w32, channel), dtype=np.float32)
    resized[0:target_h, 0:target_w, :] = proc
    target_h, target_w = target_h32, target_w32

    size_heatmap = (int(target_w/2), int(target_h/2))

    return resized, ratio, size_heatmap

def cvt2HeatmapImg(img):
    img = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    img = cv2.applyColorMap(img, cv2.COLORMAP_JET)
    return img


def sorting_bounding_box(points):
    point_sum = list(map(lambda x: [x.tolist(), x[0][1]], points))
    final_arr = []
    while len(point_sum) != 0:
        tmp_arr = [arr for arr in sorted(point_sum, key=lambda x: x[1])]
        init_box = tmp_arr[0]
        thresh_value = abs(init_box[0][0][1] - init_box[0][3][1]) / 2
        tmp_arr.remove(init_box)
        point_sum.remove(init_box)
        filter_arr = [i for i in tmp_arr if (abs(i[0][0][1] - init_box[0][0][1]) <= thresh_value)]
        for i in filter_arr:
            point_sum.remove(i)

        filter_arr = list(map(lambda x: x[0], filter_arr))
        filter_arr = [init_box[0]] + filter_arr
        # final_arr.append(sorted(filter_arr, key=lambda x: x[0][0]))
        final_arr.append(len(filter_arr))

    return final_arr
