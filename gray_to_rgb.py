#!/usr/bin/python

import cv2
import numpy as np
from random import randrange

def generateDictColors(size):
    dictColors = {}
    for i in range(size):
        while True:
            newColor = (randrange(0, 256), randrange(0, 256), randrange(0, 256))
            if not newColor in dictColors:
                break
        dictColors[i] = newColor
    return dictColors

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
