#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 14:37:10 2022

@author: poff
"""
import cv2
from pathlib import PurePosixPath
#from pathlib import Path
import pandas as pd
from shutil import copy
from shutil import move
import os
import glob
import pytesseract

path = '/home/poff/Projects/Technology/python/2022_QRcodes/2022_QRcodes'
#nonDecodedImageFiles = path + '/images/nonDecoded'
#dataPath = '/home/poff/Projects/Technology/python/2021AutomateWeb/smartid/SAMPLE_lead_codes.xlsx'
imagePath = path + '/images/optimized/'
itemListPath = path + '/data/2022_scanned_item_list.csv'
dstSuccess = 'images/decoded/'
dstFail = 'images/nonDecoded/'
dstDuplicate = 'images/duplicates/'
logPath = path + '/data/log.csv'

config = (r'--tessdata-dir "/home/poff/Programs/anaconda3/envs/qrCodes/share/tessdata" -l eng --oem 1 --psm 1')
tessdata_dir_config = r'--tessdata-dir "/home/poff/Programs/anaconda3/envs/qrCodes/share/tessdata"'

#imageFile = 'images/IMG_0066.JPG'
#imageFiles = 'images'

## Testing variable definitions
#imagePath = path + '/images/testImages'
#imageFolder = ('images/IMG_1428.JPEG', 'images/IMG_0066.JPG', 'images/IMG_0068.JPG', 'images/IMG_0070.JPG')
#imageFile = 'images/IMG_1476.JPG'
#dstSuccess = 'images/testImages/decoded/'
#itemListPath = path + '/data/testData.csv'
scannedItemInfos = []

# make a CSV list of QR codes from the decoded images
def writeToFile(itemList):
    #df = pd.DataFrame.from_dict(itemList)
    df = pd.DataFrame(itemList)
    df.to_csv(itemListPath, mode='a', header = False)
    
    
    
# Create list of QR codes and associated filenames from image files
def processImages(fileDir):
    #scannedItemInfos = []
    files = sorted(glob.glob(fileDir + '*.JPG', recursive=False))
    for i, file in enumerate(files):
        if not isDone(file):            
            item = {
                'Count': i,
                'Image ID': PurePosixPath(file).name,
                'QR Code': '',
                'isDecoded': False,
                'decoded URL': 'Unknown',
                'triedQR': False,
                'triedCurvedQR': False,
                'triedOCR': False,
                'Lucky Algorithm': 'None so far',
                }
            #item = {'Count': i}
            #item['Image ID'] = PurePosixPath(file).name
            print(item['Image ID'])
            decode(file, item)
            if item['isDecoded'] == False:
                collectImages(file, False)
            writeToFile([item])
            scannedItemInfos.append(item)
    #for item in scannedItemInfos:
    #        item['']
    writeLog(scannedItemInfos)
    return scannedItemInfos

def writeLog(itemList):
    summary = {
        'itemsDecoded' : sum([item.get('isDecoded') == True for item in itemList]),
        'itemsTotal' : len(itemList),
        'QR decoded' : sum([item.get('Lucky Algorithm') == 'QR' for item in itemList]),
        'Curved QR decoded' : sum([item.get('Lucky Algorithm') == 'Curved' for item in itemList]),
        'OCR decoded' : sum([item.get('Lucky Algorithm') == 'Tesseract OCR' for item in itemList]),
        }
    dfLog = pd.DataFrame(summary, index=[0])
    dfLog.to_csv(logPath, mode='a', header=False)
    print(str(summary['itemsDecoded']) + ' of ' + str(summary['itemsTotal']) + ' codes found, for a total success rate of ' + str(summary['itemsDecoded'] / summary['itemsTotal']* 100) + ' percent.')

def isDone(file):
    filename = PurePosixPath(file).name
    if (filename[0]).isnumeric():
        filename = filename[filename.find('IMG'):len(filename)]
    if os.path.isfile(dstSuccess + filename):
        
        return True
    else:
        return False
        
    
    

# create a list of QR codes and corresponding image filenames
# def makescannedItemInfosList (imageFolder):
#     #scannedItemInfos = []
#     imageFolder 
#     for i, image in enumerate(imageFolder):
#         filetype = PurePosixPath(image).suffix
#         if filetype == '.JPG':
#             scannedItemInfo = {'count': i}
#             scannedItemInfo['Image File'] = PurePosixPath(image).name
#             #decode(image, scannedItemInfo)
#             decodeQRFromImage(image, scannedItemInfo)
#             scannedItemInfos.append(scannedItemInfo)
#             #print(scannedItemInfo)
#         else:
#             print('filetype is not jpeg')
#     print(scannedItemInfos)
#     return scannedItemInfos

# separate images into QR code/non-QR code folders
def collectImages(file, isDecoded):
    #dstFail = 'images/nonDecoded/'
    filename = PurePosixPath(file).name
    if (filename[0]).isnumeric():
        filename = filename[filename.find('IMG'):len(filename)]
    if isDecoded:
        if not os.path.isfile(dstSuccess + filename):
            print(dstSuccess + filename)
            move(file, dstSuccess + filename)
            print('file to success')
        else:
            move(file, dstDuplicate + filename)
            print('file to duplicate')
            #print(filename + ' is a QR code')
        # if os.path.isfile(dstFail + filename):
        #     os.remove(dstFail + filename)
        #     print(filename + ' is now decoded. Congrats.')
    elif not isDecoded:
        if not os.path.isfile(dstFail + filename):
             move(file, dstFail + filename)
             print('file to fail')
             #print(filename + ' is not a QR code')
        # if os.path.isfile(dstSuccess + filename):
        #     print(filename + ' is already decoded. Dont go backwards')
        else:
            move(file, dstDuplicate + filename)
            print('file to duplicate')
    else:
        print (filename + ' is not not decoded??')
        
def decode(image, info):
    decodeMethods = [
        decodeQRFromImage,
        decodeQRFromCurvedImage,
        decodeFromOCR
        ]
    for method in decodeMethods:
        if info['isDecoded'] == False:
            method(image,info)
                
    
        
            
def decodeQRFromCurvedImage(file, item):
    detector = cv2.QRCodeDetector()
    img = cv2.imread(file)
    data, bbox, url = detector.detectAndDecodeCurved(img)
    item['triedCurvedQR'] = True
    if data == '':
        #item['isDecoded'] = False
        #item['decoded URL'] = 'Unknown'
        item['Notes Curved'] = 'No QR deciphered'
        #collectImages(file, False)
    else:
        item['decoded URL'] = data
        item['QR Code'] = PurePosixPath(data).name
        item['Lucky Algorithm'] = 'Curved'
        item['isDecoded'] = True
        collectImages(file, True)
        print('....................IT WORKED?!?................................')
    print (item)
    return item
    
# Decode QR codes from JPEG files
def decodeQRFromImage(file, item):
    detector = cv2.QRCodeDetector()
    img = cv2.imread(file)
    #bbox = detector.detect(img)
    data, bbox, url = detector.detectAndDecode(img)
    item['triedQR'] = True
    if data == '':
        item['Notes QR'] = 'No QR deciphered'
    else:
        item['decoded URL'] = data
        item['QR Code'] = PurePosixPath(data).name
        item['Lucky Algorithm'] = 'QR'
        item['isDecoded'] = True
        collectImages(file, True)
        print ('.............................QR found success')
    print (item)
    return item
    # if bbox is not None: #if QR code found, decode
    #     #data, url = detector.decode(img, bbox)
    #     #if data == '': # if unable to decode, try curved image algorithm
    #      #   data, url = detector.decodeCurved(img, bbox)
    #     if data == '': #try curved
    #         data, bbox, url = decodeQRFromCurvedImage(img)
    #         if data == '':
    #             item['decoded URL'] = 'Unknown'
    #             item['algorithm'] = 'None'
    #             collectImages(file, False)
    #         else:
    #             item['QR Code'] = PurePosixPath(data).name
    #             item['decoded URL'] = 'curved'
    #             collectImages(file, True)
    #     elif item['algorithm'] == 'None': 
    #         item['decoded URL'] = data
    #         item['QR Code'] = PurePosixPath(data).name
    #         item['algorithm'] = 'Curved'
    #         collectImages(file, True)
    #     else:
    #         item['decoded URL'] = data
    #         item['QR Code'] = PurePosixPath(data).name
    #         item['algorithm'] = 'normal'
    #         collectImages(file, True)
    # else: #if no QR found
    #     item['decoded URL'] = 'Unknown'
    #     item['algorithm'] = 'No QR found'
    #     collectImages(file, False)        
    # return item
    #except: 
     #   print('oh no. An error.')

def decodeFromOCR(file, item):
    img = cv2.imread(file)
    text = pytesseract.image_to_string(img, config=config)
    # Remove whitespaces
    textTrim = text.replace(' ','')
    URL = 'ray.com/'
    URLindex = textTrim.find(URL)
    item['triedOCR'] = True
    if URLindex == -1:
        item['Notes OCR'] = 'Code not found.'
    else:
        qrIndex = URLindex + len(URL)
        qrCode = textTrim[qrIndex:qrIndex+4]
        item['QR Code'] = qrCode
        item['decoded URL'] = 'https://smartid.bar-ray.com/' + qrCode
        item['Lucky Algorithm'] = 'Tesseract OCR'
        item['isDecoded'] = True
        collectImages(file, True)
        print ('......................OCR wins')
    return item
  

processImages(imagePath)
#scannedItemInfos = processImages(imagePath)
#scannedItemInfos()
#writeToFile(scannedItemInfos)    
