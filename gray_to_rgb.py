#!/usr/bin/python

import cv2
import numpy as np
from random import randrange
from object_labels_definition import OBJECT_LABELS_TO_ID
from object_labels_definition import ID_TO_RGB_COLOR

def generateDictColors(size,default_ids=True):
    dictColors = {}
    if default_ids:
        dictColors=ID_TO_RGB_COLOR
    else:
        for i in range(size):
            while True:
                newColor = (randrange(0, 256), randrange(0, 256), randrange(0, 256))
                if not newColor in dictColors:
                    break
            dictColors[i] = newColor
    return dictColors

def generateDictGray(objectNames,default_ids=True):
    dictGray = {}
    if default_ids:
    
        dictGray=OBJECT_LABELS_TO_ID
    else:
        for index, objectName in enumerate(objectNames):
            dictGray[objectName] = index + 1
    return dictGray

def grayToRgb(grayImage, dictColors):
    height, width = grayImage.shape
    imageColor = np.zeros((height, width, 3), np.uint8)
    channelBlue = imageColor[:, :, 0]
    channelGreen = imageColor[:, :, 1]
    channelRed = imageColor[:, :, 2]
    for key in dictColors:
        channelBlue[grayImage == (key + 1)] = dictColors[key][0]
        channelGreen[grayImage == (key + 1)] = dictColors[key][1]
        channelRed[grayImage == (key + 1)] = dictColors[key][2]
    return imageColor
