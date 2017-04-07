#!/usr/bin/python
import numpy as np
import cv2
import math
import subprocess
import random
from random import randint
from time import gmtime, strftime
from os.path import isfile

from rotate_image import rotateImage
from image_check import getImageNames
from config_file import readConfigSection, writeConfigFile
from rectangle import Rectangle

# Constants
WINDOW_NAME = "Box"
DIRNAME_OUTPUT = "output"
BACKGROUND_DIR = "./sources/background"
OBJECTS_DIR = "./sources/objects"
DO_DROP_OBJECTS = True
MAX_OBJECTS_COUNT = 3
INTERSECT_COUNTER_LIMIT = 100
DO_VARIATE_BRIGHTNESS = True

# Paramerters which can be set to default values
doCropBox = True
rescaleCoef = 1
sampleSetSize = 30
backgroundFilename = "box_white_back.jpg"

def heightAbsToRel(height, value):
	return (value / height) * 2 - 1

def widthAbsToRel(width, value):
        return (value / width) * 2 - 1

def getObjectImages(parentDirectory):
    imageNames = getImageNames(parentDirectory)
    objectImages = []
    for filename in imageNames:
        imagePath = parentDirectory + "/" + filename
        imageFull = cv2.imread(imagePath, cv2.IMREAD_UNCHANGED)
        height, width, numChannels = imageFull.shape
        if numChannels > 3:
            imageMask = imageFull[:, :, 3]
            imageRed = imageFull[:,:,0]
            imageGreen = imageFull[:,:,1]
            imageBlue = imageFull[:,:,2]
            imageRed[imageMask != 255] = 0
            imageGreen[imageMask != 255] = 0
            imageBlue[imageMask != 255] = 0
            imageRgb = np.zeros((height, width, 3), dtype = np.uint8)
            imageRgb[:,:,0] = imageRed
            imageRgb[:,:,1] = imageGreen
            imageRgb[:,:,2] = imageBlue
        else:
            imageRgb = imageFull
        objectImages.append(imageRgb)
    return (objectImages, imageNames)

def getImageBackground(backgroundDir, backgroundFilename, doCropBox):
    backgroundPath = backgroundDir + "/" + backgroundFilename
    if not isfile(backgroundPath):
        print("Error: no such file " + backgroundPath)
        return np.zeros((0, 0, 3), np.uint8)

    imageBackground = cv2.imread(backgroundPath, cv2.IMREAD_UNCHANGED)
    dictBoxBorders = readConfigSection(BACKGROUND_DIR, backgroundFilename)

    boxTop = np.int(dictBoxBorders["top"])
    boxBottom = np.int(dictBoxBorders["bottom"])
    boxLeft = np.int(dictBoxBorders["left"])
    boxRight = np.int(dictBoxBorders["right"])
    imageBox = imageBackground[boxTop:boxBottom, boxLeft:boxRight, :]
    return imageBox

def putObjectOnBackground(imageBoxCurret, objImage, borders):
    xBeg = borders[0]
    yBeg = borders[1]
    xEnd = borders[2]
    yEnd = borders[3]

    imageGrey = cv2.cvtColor(objImage, cv2.COLOR_BGR2GRAY)
    imageRed = objImage[:,:,0]
    imageGreen = objImage[:,:,1]
    imageBlue = objImage[:,:,2]

    imageArea = imageBoxCurrent[yBeg:yEnd, xBeg:xEnd, :]
    imageAreaRed = imageArea[:,:,0]
    imageAreaGreen = imageArea[:,:,1]
    imageAreaBlue = imageArea[:,:,2]

    imageAreaRed[imageGrey != 0] = imageRed[imageGrey != 0]
    imageAreaGreen[imageGrey != 0] = imageGreen[imageGrey != 0]
    imageAreaBlue[imageGrey != 0] = imageBlue[imageGrey != 0]

def addSquareToList(top, bottom, left, right, listSquares):
    listSquares.append({"top" : top, 
        "bottom" : bottom,
        "left" : left,
        "right" : right })

def decideTakenImages(numImages):
    isImageTaken = [False] * numImages
    for i in range(MAX_OBJECTS_COUNT):
        indexTrue = random.randint(0, numImages - 1)
        isImageTaken[indexTrue] = True
    return isImageTaken

def putImagesOnBackground(imageBoxCurrent, objectImages, imageNames):
    height, width, numChannels = imageBoxCurrent.shape
    dictObjects = {}
    listRectangles = []
    isImageTaken = decideTakenImages(len(objectImages))
    for i in range(len(objectImages)):
        if not DO_DROP_OBJECTS:
            doSkipObject = False
        else:
            doSkipObject = not isImageTaken[i]

        objectImage = objectImages[i]
        objectName = imageNames[i]
        if not doSkipObject:
            heightOrig, widthOrig, channelsOrig = objectImage.shape
            angle = randint(0, 359)
            (imageRotated, cornersRot) = rotateImage(objectImage, angle / 180.0 * math.pi)
            objHeight, objWidth, objChannels = imageRotated.shape
            if objHeight > height or objWidth > width:
                print "Warning: object does not fit into the box"
                continue

            intersectCounter = 0
            while True:
                xBeg = randint(0, width - objWidth)
                yBeg = randint(0, height - objHeight)
                xEnd = xBeg + objWidth
                yEnd = yBeg + objHeight
                rectCurrent = Rectangle(yBeg, yEnd, xBeg, xEnd)
                doesIntersect = rectCurrent.doesIntersectRectangles(listRectangles)
                if not doesIntersect:
                    listRectangles.append(rectCurrent)
                    break
                else:
                    intersectCounter += 1
                    if intersectCounter >= INTERSECT_COUNTER_LIMIT:
                        doSkipObject = True
                        break
 
            if not doSkipObject:
                xCenter = (xBeg + xEnd) / 2.0
                yCenter = (yBeg + yEnd) / 2.0

                putObjectOnBackground(imageBoxCurrent, imageRotated, \
                    [xBeg, yBeg, xEnd, yEnd])

        dictObjects[objectName] = {}
        dictObjects[objectName]["is_present"] = 0.0 if doSkipObject else 1.0
        dictObjects[objectName]["angle"] = (angle / 180.0) if not doSkipObject else 0.0
        dictObjects[objectName]["x"] = xCenter if not doSkipObject else 0.0
        dictObjects[objectName]["y"] = yCenter if not doSkipObject else 0.0
        dictObjects[objectName]["x_rel"] = (xCenter / width) * 2 - 1 if not doSkipObject else 0.0
	dictObjects[objectName]["y_rel"] = (yCenter / height) * 2 - 1 if not doSkipObject else 0.0
        dictObjects[objectName]["height"] = heightOrig if not doSkipObject else 0
        dictObjects[objectName]["width"] = widthOrig if not doSkipObject else 0

        dictObjects[objectName]["x_left_top"] = widthAbsToRel(width, xCenter + cornersRot[0][0]) \
                if not doSkipObject else 0.0
        dictObjects[objectName]["y_left_top"] = heightAbsToRel(height, yCenter + cornersRot[0][1]) \
                if not doSkipObject else 0.0

        dictObjects[objectName]["x_right_top"] = widthAbsToRel(width, xCenter + cornersRot[1][0]) \
                if not doSkipObject else 0.0
        dictObjects[objectName]["y_right_top"] = heightAbsToRel(height, yCenter + cornersRot[1][1]) \
                if not doSkipObject else 0.0

        dictObjects[objectName]["x_left_bottom"] = widthAbsToRel(width, xCenter + cornersRot[2][0]) \
                if not doSkipObject else 0.0
        dictObjects[objectName]["y_left_bottom"] = heightAbsToRel(height, yCenter + cornersRot[2][1]) \
                if not doSkipObject else 0.0

        dictObjects[objectName]["x_right_bottom"] = widthAbsToRel(width, xCenter + cornersRot[3][0]) \
                if not doSkipObject else 0.0
        dictObjects[objectName]["y_right_bottom"] = heightAbsToRel(height, yCenter + cornersRot[3][1]) \
                if not doSkipObject else 0.0
 
    return dictObjects


def scaleCoordinates(dictObjects, factor):
    for key in dictObjects:
        dictObjects[key]["x"] = round(dictObjects[key]["x"] * factor)
        dictObjects[key]["y"] = round(dictObjects[key]["y"] * factor)
        dictObjects[key]["height"] = round(dictObjects[key]["height"] * factor)
        dictObjects[key]["width"] = round(dictObjects[key]["width"] * factor)

def variateBrightness(img):
    incr = random.randint(-60, 60)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    value = hsv[:,:,2]
    if incr >= 0:
        incr_border = 255 - incr
        value[value >= incr_border] = 255
        value[value < incr_border] += incr
    else:
        incr_border = -incr
        value[value > incr_border] -= incr_border
        value[value <= incr_border] = 0
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return img

imageBox = getImageBackground(BACKGROUND_DIR, backgroundFilename, doCropBox)
objectImages, imageNames = getObjectImages(OBJECTS_DIR)
stringTime = strftime("%Y%m%d_%H%M%S", gmtime())
dirnameOutputFull = DIRNAME_OUTPUT + "/" + stringTime
subprocess.call(["mkdir", "-p", dirnameOutputFull])

descPictures = {}
for i in range(sampleSetSize):
    imageBoxCurrent = imageBox.copy()
    dictObjects = putImagesOnBackground(imageBoxCurrent, objectImages, imageNames)
    if rescaleCoef != 1.0:
        imageBoxCurrent = cv2.resize(imageBoxCurrent, (0, 0), fx = rescaleCoef, fy = rescaleCoef)
        scaleCoordinates(dictObjects, rescaleCoef)
    if DO_VARIATE_BRIGHTNESS:
        imageBoxCurrent = variateBrightness(imageBoxCurrent)
    imageBoxCurrent = cv2.GaussianBlur(imageBoxCurrent, (5, 5), 0)

    outImageName = str(i) + ".png"
    outImagePath = dirnameOutputFull + "/" + outImageName
    cv2.imwrite(outImagePath, imageBoxCurrent)

    descPictures[outImageName] = dictObjects

writeConfigFile(dirnameOutputFull, descPictures)
