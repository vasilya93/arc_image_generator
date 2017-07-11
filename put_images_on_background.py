#!/usr/bin/env python

import cv2
import random

import numpy as np

from random import randint
from random import shuffle
from rectangle import Rectangle
from rotate_image import rotateImage
from object_image_description import ObjectImageDescription
from put_object_on_background import putObjectOnBackground

# The function randomly selects images from the list 'objectImages' and places
# them on the background of 'imageBoxCurrent' with random position and
# orientation trying to avoid intersections.
def putImagesOnBackground(imageBoxCurrent, dictObjectImages, objectNames, paramConfig, imageMarkup = None):
    height, width, numChannels = imageBoxCurrent.shape
    dictObjects = {}
    listRectangles = []
    isImageTaken = decideTakenImages(len(objectNames), paramConfig.MAX_OBJECTS_COUNT)

    # shuffling images of the objects, so that we do not take them
    # in the same order every time
    imageIndeces = range(len(objectNames))
    shuffle(imageIndeces)

    for i in imageIndeces:
        objDesc = ObjectImageDescription()
        objDesc.imageWidth = width
        objDesc.imageHeight = height
        if not paramConfig.DO_DROP_OBJECTS:
            objDesc.isPresent = True
        else:
            objDesc.isPresent = isImageTaken[i]

        objectName = objectNames[i]
        numObjectImages = len(dictObjectImages[objectName])
        currentObjectImageIndex = random.randint(0, numObjectImages - 1)
        objectImage = dictObjectImages[objectName][currentObjectImageIndex]

        if paramConfig.DO_RESCALE_OBJECTS:
            rescaleX = random.uniform(1 - paramConfig.OBJECT_SCALE_VARIATION, \
                    1 + paramConfig.OBJECT_SCALE_VARIATION)
            if paramConfig.RESCALE_KEEP_RATE:
                rescaleY = rescaleX
            else:
                rescaleY = random.uniform(1 - paramConfig.OBJECT_SCALE_VARIATION, \
                        1 + paramConfig.OBJECT_SCALE_VARIATION)

            objectImage = cv2.resize(objectImage, None, fx = rescaleX, \
                    fy = rescaleY)

        cornersRot = []
        if objDesc.isPresent:
            objDesc.height, objDesc.width, channelsOrig = objectImage.shape

            # Rotating image of the object and checking whether the size is good
            imageRotated, cornersRot, objHeight, objWidth = rotateObjectImage(objDesc, \
                  objectImage, \
                  height, \
                  width, \
                  paramConfig.DO_PUT_DENSELY, \
                  paramConfig.OVERSIZE_COUNTER_LIMIT, \
                  paramConfig.DO_ROTATE_OBJECTS)

        # Selecting position for rotated object, and checking that there is
        # no intersection with the other objects
        if objDesc.isPresent:
            objMarkup = cv2.cvtColor(imageRotated, cv2.COLOR_BGR2GRAY)
            objMarkup[objMarkup > 0] = i + 1
            selectObjectPosition(objMarkup, objDesc, height, width, objHeight, objWidth, \
                    listRectangles, imageMarkup, paramConfig.DO_PUT_DENSELY, paramConfig.INTERSECT_COUNTER_LIMIT)

        # Once the object is rotated and its position is selected, we put it
        # onto the image
        if objDesc.isPresent:
            objDesc.x = (objDesc.xBeg + objDesc.xEnd) / 2.0
            objDesc.y = (objDesc.yBeg + objDesc.yEnd) / 2.0

            putObjectOnBackground(imageBoxCurrent, imageRotated, \
                [objDesc.xBeg, objDesc.yBeg, objDesc.xEnd, objDesc.yEnd], i + 1, imageMarkup)

        dictObjects[objectName] = objDesc.getDictionary(cornersRot)
 
    return dictObjects

# Returns array of boolean values of indicated size, where some random of the
# elements are set to true, and the rest are false. Maximal number of true
# values is equal to MAX_OBJECTS_COUNT. The function is supposed to be used for
# random selection of object which will be put into an image.
def decideTakenImages(numImages, maxObjectsCount):
    isImageTaken = [False] * numImages
    for i in range(maxObjectsCount):
        indexTrue = random.randint(0, numImages - 1)
        isImageTaken[indexTrue] = True
    return isImageTaken

def rotateObjectImage(objDesc, objectImage, height, width, doPutDensely, oversizeCounterLimit, doRotateObject):
    oversizeCounter = 0
    imageRotated = None
    while True:
        if not doRotateObject:
            objDesc.angle = 0
        elif doPutDensely:
            objDesc.angle = randint(0, 79)
            if objDesc.angle > 70:
                objDesc.angle += 280
            elif objDesc.angle > 50:
                objDesc.angle += 210
            elif objDesc.angle > 30:
                objDesc.angle += 140
            elif objDesc.angle > 10:
                objDesc.angle += 70
        else:
            objDesc.angle = randint(0, 359)
        (imageRotated, cornersRot) = rotateImage(objectImage, \
                objDesc.angle / 180.0 * np.pi)
        objHeight, objWidth, objChannels = imageRotated.shape
        if objHeight > height or objWidth > width:
            oversizeCounter += 1
            if oversizeCounter >= oversizeCounterLimit:
                print "Warning: object does not fit into the box"
                objDesc.isPresent = False
                break
        else:
            break
    return (imageRotated, cornersRot, objHeight, objWidth)

def selectObjectPosition(objMarkup, objDesc, height, width, objHeight, objWidth, \
        listRectangles, imageMarkup, doPutDensely, intersectCounterLimit):
    if doPutDensely:
        selectPositionDense(objMarkup, objDesc, height, width, objHeight, objWidth, \
            listRectangles, imageMarkup)
    else:
        selectPositionRandom(objDesc, height, width, objHeight, objWidth, \
            listRectangles, intersectCounterLimit)

def selectPositionRandom(objDesc, height, width, objHeight, objWidth, \
        listRectangles, intersectCounterLimit):
    intersectCounter = 0
    while True:
        objDesc.xBeg = randint(0, width - objWidth)
        objDesc.yBeg = randint(0, height - objHeight)
        objDesc.xEnd = objDesc.xBeg + objWidth
        objDesc.yEnd = objDesc.yBeg + objHeight
        rectCurrent = Rectangle(objDesc.yBeg, objDesc.yEnd, objDesc.xBeg, objDesc.xEnd)
        doesIntersect = rectCurrent.doesIntersectRectangles(listRectangles) or \
                rectCurrent.doesOverlapRectangles(listRectangles)
        if not doesIntersect:
            listRectangles.append(rectCurrent)
            break
        else:
            intersectCounter += 1
            if intersectCounter >= intersectCounterLimit:
                print "Warning: object intersects the other objects"
                objDesc.isPresent = False
                break

def selectPositionDense(objMarkup, objDesc, height, width, objHeight, objWidth, \
        listRectangles, imageMarkup):
        x_range = width - objWidth
        y_range = height - objHeight

        num_samples = 10
        x_values = np.round(np.linspace(0, x_range, num_samples))
        y_values = np.round(np.linspace(0, y_range, num_samples))
        x_values = x_values.astype(int)
        y_values = y_values.astype(int)

        grid_x, grid_y = np.meshgrid(x_values, y_values)

        min_overlap = sys.maxint
        min_overlap_x = -1
        min_overlap_y = -1
        for i in range(num_samples):
            for j in range(num_samples):
                x_current = grid_x[i, j]
                y_current = grid_y[i, j]
                x_end = x_current + objWidth
                y_end = y_current + objHeight

                overlap = getOverlap(imageMarkup, objMarkup, \
                        x_current, y_current, x_end, y_end)
                if overlap < min_overlap:
                    min_overlap = overlap
                    min_overlap_x = x_current
                    min_overlap_y = y_current

        objDesc.xBeg = min_overlap_x
        objDesc.yBeg = min_overlap_y
        objDesc.xEnd = min_overlap_x + objWidth
        objDesc.yEnd = min_overlap_y + objHeight
