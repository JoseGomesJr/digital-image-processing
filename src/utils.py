#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 10:56:09 2019

@author: tvieira
"""
import cv2
import numpy as np
import matplotlib.pyplot as plt

def norm_img(img):
    out = np.zeros(img.shape, np.float64)
    cv2.normalize(img.astype('float64'), out, 1, 0, cv2.NORM_MINMAX)
    return out

def do_nothing(x):
    pass

def plot_grayscale_histogram(gray_img):
    plt.hist(gray_img.ravel(), 256, [0, 256])
    plt.show()

def plot_rgb_histogram(rgb_img):
    color = ('r', 'g', 'b')
    for i, col in enumerate(color):
        hist = cv2.calcHist([rgb_img], [i], None, [256], [0, 256])
        plt.plot(hist, color=col)
        plt.xlim([0, 256])
    plt.show()
    return None
    
def plot_histogram(img):
    # Grayscale image
    if len(img.shape) == 2:
        hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        plt.plot(hist, color='k')
        plt.show()
    # Color image
    elif len(img.shape) == 3:
        color = ('r', 'g', 'b')
        for i, col in enumerate(color):
            hist = cv2.calcHist([img], [i], None, [256], [0, 256])
            plt.plot(hist, color=col)
            plt.xlim([0, 256])
    plt.show()
    return None

def create_noisy_img(shape, noise_type = 'uniform', a=127, b=40):
    tmp = np.zeros(shape, dtype=np.uint8)
    if noise_type == 'uniform':
        noise = cv2.merge([cv2.randu(x, a, b) for x in cv2.split(tmp)])
    elif noise_type == 'normal':
        noise = cv2.merge([cv2.randn(x, a, b) for x in cv2.split(tmp)])
    return noise

def im_info(img):
    print('# Image info:')
    print(f'Image type = {img.dtype.name}')
    h, w = img.shape
    d = img.ndim
    print(f'[Height, Width, Dimensions] = [{h}, {w}, {d}]')
    print(f'Max value = {img.max()}')
    print(f'Mean value = {img.mean():.2f}')
    print(f'Min value = {img.min()}')
    print('\n\n')
    return None

def compute_histogram_1C(src):
    # Compute the histograms:
    b_hist = cv2.calcHist([src], [0], None, [256], [0, 256], True, False)

    # Draw the histograms for B, G and R
    hist_w = 512
    hist_h = 400
    bin_w = np.round(hist_w / 256)

    histImage = np.ones((hist_h, hist_w), np.uint8)

    # Normalize the result to [ 0, histImage.rows ]
    cv2.normalize(b_hist, b_hist, 0, histImage.shape[0], cv2.NORM_MINMAX)

    # Draw for each channel
    for i in range(1, 256):
        cv2.line(histImage, (int(bin_w * (i - 1)), int(hist_h - np.round(b_hist[i - 1]))),
                 (int(bin_w * i), int(hist_h - np.round(b_hist[i]))), 255, 2, cv2.LINE_8, 0)
    return histImage#, b_hist

def compute_histogram_3C(src):

    b, g, r = cv2.split(src)

    # Compute the histograms:
    b_hist = cv2.calcHist([b], [0], None, [256], [0, 256], True, False)
    g_hist = cv2.calcHist([g], [0], None, [256], [0, 256], True, False)
    r_hist = cv2.calcHist([r], [0], None, [256], [0, 256], True, False)

    # Draw the histograms for B, G and R
    hist_w = 512
    hist_h = 200
    bin_w = np.round(hist_w / 256)

    histImage = np.zeros((hist_h, hist_w, 3), np.uint8)

    # Normalize the result to [ 0, histImage.rows ]
    cv2.normalize(b_hist, b_hist, 0, histImage.shape[0], cv2.NORM_MINMAX)
    cv2.normalize(g_hist, g_hist, 0, histImage.shape[0], cv2.NORM_MINMAX)
    cv2.normalize(r_hist, r_hist, 0, histImage.shape[0], cv2.NORM_MINMAX)

    # Draw for each channel
    for i in range(1, 256):
        cv2.line(histImage, (int(bin_w * (i - 1)), int(hist_h - np.round(b_hist[i - 1]))),
                 (int(bin_w * i), int(hist_h - np.round(b_hist[i]))), (255,0,0), 2, cv2.LINE_8, 0)
        cv2.line(histImage, (int(bin_w * (i - 1)), int(hist_h - np.round(g_hist[i - 1]))),
                 (int(bin_w * i), int(hist_h - np.round(g_hist[i]))), (0,255,0), 2, cv2.LINE_8, 0)
        cv2.line(histImage, (int(bin_w * (i - 1)), int(hist_h - np.round(r_hist[i - 1]))),
                 (int(bin_w * i), int(hist_h - np.round(r_hist[i]))), (0,0,255), 2, cv2.LINE_8, 0)
        
    return histImage#, b_hist, g_hist, r_hist

def compute_piecewise_linear_val(val, r1, s1, r2, s2):
    output = 0
    if (0 <= val) and (val <= r1):
        output = (s1 / r1) * val
    elif (r1 <= val) and (val <= r2):
        output = ((s2 - s1) / (r2 - r1)) * (val - r1) + s1
    elif (r2 <= val) and (val <= 1):
        output = ((1 - s2) / (1 - r2)) * (val - r2) + s2

    return output

def get_piecewise_transformed_img (img, r1, s1, r2, s2):
    
    if img.dtype == 'uint8':
        out = img/255.
    else:
        img.copy()
    
    eps = 1e-16
    
    mask1 = out <= r1
    mask2 = np.bitwise_and(r1 < out, out <= r2)
    mask3 = out > r2
    #Opitionally check whether masks are mutually exclusive:
    mask = np.bitwise_xor(mask1, np.bitwise_xor(mask2, mask3))
    print(f"Mutually exclusive masks? {mask.all()}")
    
    out[mask1] = out[mask1] * (s1 / (r1 + eps))
    out[mask2] = s1 + (out[mask2] - r1) * ((s2 - s1)/(r2 - r1 + eps))
    out[mask3] = s2 + (out[mask3] - r2) / (1 - r2 + eps)
    
    out = np.clip(out, 0, 1.)
    out = 255*out
    out = out.astype('uint8')
    
    return out

def log_transform(img):
    img2 = np.copy(img)
    img2 = np.log(1 + img2)
    return img2