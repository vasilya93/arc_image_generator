import random
import cv2

import numpy as np

from random import randint
from copy import deepcopy
from random import shuffle

from rotate_image import rotateImage
from put_images_on_background import decideTakenImages
from put_object_on_background import putObjectOnBackground

MAX_CLUTTER_OBJECTS_COUNT = 10

# should return two images: the first is generated image, the second is markup image
def generateObjectFocusedImage(imagesObject, imagesClutter, imageBackground):
    maxObjectsCount = max([MAX_CLUTTER_OBJECTS_COUNT, len(imagesClutter)])
    isImageTaken = decideTakenImages(len(imagesClutter), maxObjectsCount)

    imageIndeces = range(len(imagesClutter))
    shuffle(imageIndeces)

    bgHeight, bgWidth, bgChannels = imageBackground.shape

    for i in imageIndeces:
        if not isImageTaken[i]:
            continue

        imageObject = imagesClutter[i]

        objectRescaleCoef = random.uniform(0.7, 1.3)
        imageObject = cv2.resize(imageObject, None, fx = objectRescaleCoef, \
            fy = objectRescaleCoef)

        didFit, imageRotated, cornersRot, objHeight, objWidth = rotateImageRandomAngle(imageObject, \
            bgHeight, \
            bgWidth, \
            doPutDensely = False)

        if not didFit:
            continue

        objectPosition = selectObjectPosition(bgHeight, bgWidth, objHeight, objWidth)

        putObjectOnBackground(imageBackground, imageRotated, \
            objectPosition)

    imageMask = np.zeros((bgHeight, bgWidth), np.uint8)

    # adding the last object

    indexImageObject = randint(0, len(imagesObject) - 1)
    imageObject = imagesObject[indexImageObject]

    objectRescaleCoef = random.uniform(0.7, 1.3)
    imageObject = cv2.resize(imageObject, None, fx = objectRescaleCoef, \
            fy = objectRescaleCoef)

    didFit, imageRotated, cornersRot, objHeight, objWidth = rotateImageRandomAngle(imageObject, \
        bgHeight, \
        bgWidth, \
        doPutDensely = False)

    if didFit:
        objectPosition = selectObjectPosition(bgHeight, bgWidth, objHeight, objWidth)

        putObjectOnBackground(imageBackground, imageRotated, \
            objectPosition, 255, imageMask)

    return (imageBackground, imageMask)

def rotateImageRandomAngle(objectImage, backgroundHeight, backgroundWidth, doPutDensely):
    OVERSIZE_COUNTER_LIMIT = 100
    oversizeCounter = 0
    imageRotated = None
    didFit = False
    while True:
        if doPutDensely:
            angle = randint(0, 79)
            if angle > 70:
                angle += 280
            elif angle > 50:
                angle += 210
            elif angle > 30:
                angle += 140
            elif angle > 10:
                angle += 70
        else:
            angle = randint(0, 359)
        (imageRotated, cornersRot) = rotateImage(objectImage, \
                angle / 180.0 * np.pi)
        objHeight, objWidth, objChannels = imageRotated.shape
        if objHeight > backgroundHeight or objWidth > backgroundWidth:
            oversizeCounter += 1
            if oversizeCounter >= OVERSIZE_COUNTER_LIMIT:
                print "Warning: object does not fit into the box"
                break
        else:
            didFit = True
            break
    return (didFit, imageRotated, cornersRot, objHeight, objWidth)

def selectObjectPosition(bgHeight, bgWidth, objHeight, objWidth):
        xBeg = randint(0, bgWidth - objWidth)
        yBeg = randint(0, bgHeight - objHeight)
        xEnd = xBeg + objWidth
        yEnd = yBeg + objHeight
        return [xBeg, yBeg, xEnd, yEnd]
