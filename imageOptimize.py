#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 14:57:57 2022

@author: poff
"""
import cv2
import pytesseract
import numpy as np
tessdata_dir_config = r'--tessdata-dir "/home/poff/Programs/anaconda3/envs/qrCodes/share/tessdata"'
#pytesseract.image_to_string(image, lang='chi_sim', config=tessdata_dir_config)
# pytesseract path
#pytesseract.pytesseract.tesseract_cmd = ''

path = '/home/poff/Projects/Technology/python/2022_QRcodes/2022_QRcodes'
imageDir = '/images/'
imageFile = 'IMG_1430.JPG'
config = (r'--tessdata-dir "/home/poff/Programs/anaconda3/envs/qrCodes/share/tessdata" -l eng --oem 1 --psm 3')
imgDstPath = '/images/optimized/'


def findRect(file):
    print(path + imageDir + file)
    img = cv2.imread(path + imageDir + file)
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    print(thresh)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    i = 0
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        center, size, angle = rect[0], rect[1], rect[2]
        if size[0] > 100:
            i += 1
            center, size = tuple(map(int, center)), tuple(map(int, size))
            mat = cv2.getRotationMatrix2D(center, angle, 1)            
            rotated = cv2.warpAffine(imgray, mat, (img.shape[1], img.shape[0]))
            #isRotSaved = cv2.imwrite(path + imgDstPath + str(i) + 'rotated' + file, rotated)
            cropped = cv2.getRectSubPix(rotated, size, center)
            isSaved = cv2.imwrite(path + imgDstPath + str(i) + file, cropped)
            print(size[0], i, isSaved)
    
findRect(imageFile)

# def optimizeImage(file):
#     print(path + imageDir + file)
#     img = cv2.imread(path + imageDir + file)
#     # Convert to grayscale
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     isGray = cv2.imwrite(path + imgDstPath + 'gray_' + file, gray)
#     # OTSU Thresholding
#     ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
#     #isThreshold = cv2.imwrite(path + imgDstPath + 'threshold_' + file, thresh1)
#     # Define rectangle
#     rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 30))
#     #isRect = cv2.imwrite(path + imgDstPath + 'rect_' + file, rect_kernel)
#     dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
#     # Find contours
#     #contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
#     contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
#     # Save altered image as copy
#     img2 = img.copy()
#     #print(path + imgDstPath + file)
#     #cv2.imwrite(path + imgDstPath + file, img2)
#     cropped = object()
#     i = 1
#     for cnt in contours:
#         i += 1
#         x, y, w, h = cv2.boundingRect(cnt)
#         # Draw rectangle
#         cropped = img2[y:y + h, x:x + w]
#         print(x, y, w, h)
#         # Apply OCR
#         text = pytesseract.image_to_string(cropped)
#         textTrimmed = text.replace(' ','')
#         print(textTrimmed)
#         #isSaved = cv2.imwrite(path + imgDstPath + str(i) + file, cropped)
#         #print(isSaved)
    
#optimizeImage(imageFile)

