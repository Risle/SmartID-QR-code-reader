#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 14:57:57 2022

@author: poff
"""
import cv2
import pytesseract
import numpy as np
import glob
import pandas as pd
from pathlib import PurePosixPath
tessdata_dir_config = r'--tessdata-dir "/home/poff/Programs/anaconda3/envs/qrCodes/share/tessdata"'
#pytesseract.image_to_string(image, lang='chi_sim', config=tessdata_dir_config)
# pytesseract path
#pytesseract.pytesseract.tesseract_cmd = ''

path = '/home/poff/Projects/Technology/python/2022_QRcodes/2022_QRcodes'
imageDir = '/images/'
imageFile = 'IMG_1430.JPG'
imgDstPath = '/images/optimized/'
logOptPath = path + '/data/log_image_opt.csv'

optimizedImages = []

def processOptImages(fileDir):
    #scannedItemInfos = []
    files = sorted(glob.glob(fileDir + '/*.JPG', recursive=False))
    for i, file in enumerate(files):
        filename = PurePosixPath(file).name
        item = {
            'Count': i,
            'Image ID': filename,
            'Number of subImages': 0
            }
        print(item['Image ID'])
        findRect(filename, item)
        optimizedImages.append(item)
    writeLog(optimizedImages)


def writeLog(itemList):
    dfLog = pd.DataFrame(itemList)
    dfLog.to_csv(logOptPath, mode='a')
    print('log made for ' + str(len(itemList)) + ' optimized images')


def findRect(file, item):
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
        if size[0] > 200:
            i += 1
            #box = cv2.boxPoints(rect)
            #box = np.int0(box)
            #center = rect[0]
            #angle = rect[2]
            #width = rect[1][0]
            #height = rect[1][1]
            #cv2.drawContours(img, [box], cnt)
            center, size = tuple(map(int, center)), tuple(map(int, size))
            mat = cv2.getRotationMatrix2D(center, angle, 1)
            #size = rect[1]
            
            rotated = cv2.warpAffine(imgray, mat, (img.shape[1], img.shape[0]))
            #isRotSaved = cv2.imwrite(path + imgDstPath + str(i) + 'rotated' + file, rotated)
            cropped = cv2.getRectSubPix(rotated, size, center)
            isSaved = cv2.imwrite(path + imgDstPath + str(i) + file, cropped)
            item['Number of subImages'] = i
            print(size[0], i, isSaved)
            
    
#findRect(imageFile)


#processOptImages(path + imageDir)

def collectImages():
    #dstFail = 'images/nonDecoded/'
    filename = '123IMG567.JPG'
    if (filename[0]).isnumeric():
        filename = filename[filename.find('IMG'):len(filename)]
    print(filename)
        
collectImages()
def optimizeImage(file):
    print(path + imageDir + file)
    img = cv2.imread(path + imageDir + file)
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    isGray = cv2.imwrite(path + imgDstPath + 'gray_' + file, gray)
    # OTSU Thresholding
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    #isThreshold = cv2.imwrite(path + imgDstPath + 'threshold_' + file, thresh1)
    # Define rectangle
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 30))
    #isRect = cv2.imwrite(path + imgDstPath + 'rect_' + file, rect_kernel)
    dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
    # Find contours
    #contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # Save altered image as copy
    img2 = img.copy()
    #print(path + imgDstPath + file)
    #cv2.imwrite(path + imgDstPath + file, img2)
    cropped = object()
    i = 1
    for cnt in contours:
        i += 1
        x, y, w, h = cv2.boundingRect(cnt)
        # Draw rectangle
        cropped = img2[y:y + h, x:x + w]
        print(x, y, w, h)
        # Apply OCR
        text = pytesseract.image_to_string(cropped)
        textTrimmed = text.replace(' ','')
        print(textTrimmed)
        #isSaved = cv2.imwrite(path + imgDstPath + str(i) + file, cropped)
        #print(isSaved)
    
#optimizeImage(imageFile)

def decodeFromOCR(image):
    img = cv2.imread(image)
    text = pytesseract.image_to_string(img, config=config)
    URL = 'ray.com/'
    URLindex = text.find(URL)
    if URLindex == -1:
        print ('not found')
    else:
        qrIndex = URLindex + len(URL)
        #for char in text[qrIndex:qrIndex+4]:    
        qrCode = text[qrIndex:qrIndex+4]
        if qrCode.isalnum():
            print (qrCode)
        else:
            print ('QR code incorrect: ' + qrCode)
    
#decodeFromOCR(imageFile)





## Test storing data
def doThing1(a):
    a['item is done'] = False
    print(a['item is done'])
    return a
    
def doThing2(b):
    b['item is done'] = True
    print(b['item is done'])
    
def doThing3(c):
    c['item is done'] = False
    print(c['item is done'])
    
def tryThings():
    thing = {
        'item is done': False
        }
    thingArray = [
        doThing1,
        doThing2,
        doThing3]
    for doThing in thingArray:
        if thing['item is done'] == False:
            doThing(thing)
    #return thingArray[0](thing)
    return thing

#print(tryThings())