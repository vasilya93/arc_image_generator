#!/usr/bin/python

import cv2
import numpy as np

# Puts specified image of object onto specified image of background
# in indicated position considering transparancy of the image of the
# object.
def putObjectOnBackground(imageBoxCurrent, objImage, borders):
    xBeg = borders[0]
    yBeg = borders[1]
    xEnd = borders[2]
    yEnd = borders[3]
    height, width, channels = objImage.shape
    imageRed = objImage[:,:,0]
    imageGreen = objImage[:,:,1]
    imageBlue = objImage[:,:,2]
    if channels > 3:
        imageMask = objImage[:, :, 3]
        opacity = np.sum(imageMask) / np.count_nonzero(imageMask) / 255.0
    else:
        imageMask = cv2.cvtColor(objImage, cv2.COLOR_BGR2GRAY)
        imageMask[imageMask > 0] = 255
        opacity = 1.0

    imageArea = imageBoxCurrent[yBeg:yEnd, xBeg:xEnd, :]
    imageAreaRed = imageArea[:,:,0]
    imageAreaGreen = imageArea[:,:,1]
    imageAreaBlue = imageArea[:,:,2]

    imageRed[imageMask <= 0] = imageAreaRed[imageMask <= 0]
    imageGreen[imageMask <= 0] = imageAreaGreen[imageMask <= 0]
    imageBlue[imageMask <= 0] = imageAreaBlue[imageMask <= 0]

    imageObject = np.zeros([yEnd - yBeg, xEnd - xBeg, 3], np.uint8)
    imageObject[:, :, 0] = imageRed[:, :]
    imageObject[:, :, 1] = imageGreen[:, :]
    imageObject[:, :, 2] = imageBlue[:, :]

    imageAreaNew = cv2.addWeighted(imageArea, 1 - opacity, \
            imageObject, opacity, 0)

    imageArea[:,:,0] = imageAreaNew[:, :, 0]
    imageArea[:,:,1] = imageAreaNew[:, :, 1]
    imageArea[:,:,2] = imageAreaNew[:, :, 2]
