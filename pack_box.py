#!/usr/bin/python
import numpy as np
import cv2
import math
import subprocess
import random
import os
import time
from random import randint
from random import shuffle
from time import gmtime, strftime
from os.path import isfile, splitext

from rotate_image import rotateImage
from image_check import getImageNames
from config_file import readConfigSection, writeConfigFile
from put_object_on_background import putObjectOnBackground
from rectangle import Rectangle
from object_image_description import ObjectImageDescription
from gray_to_rgb import grayToRgb, generateDictColors

# Constants
WINDOW_NAME = "Box"
DIRNAME_OUTPUT = "output"
DIRNAME_OUT_IMAGES = "images"
DIRNAME_OUT_MARKUP = "markup"
BACKGROUND_DIR = "./sources/background"
OBJECTS_DIR = "./sources/objects"
INTERSECT_COUNTER_LIMIT = 100
OVERSIZE_COUNTER_LIMIT = 100

DO_DROP_OBJECTS = True
MAX_OBJECTS_COUNT = 3
DO_VARIATE_BRIGHTNESS = False
DO_WRITE_MARKUP = False

# Paramerters which can be set to default values
DO_CROP_BOX = True
RESCALE_COEF = 1.0
SAMPLE_SET_SIZE = 30
BACKGROUND_FILENAME = "box_white.jpg"

DO_WRITE_LOG_FILE = True

logFile = None

# Returns list of images (of objects) and names of the images from
# the directory which is given as parameter to the function.
def getObjectImages(parentDirectory):
    imageNames = getImageNames(parentDirectory)
    objectImages = []
    for filename in imageNames:
        imagePath = parentDirectory + "/" + filename
        imageFull = cv2.imread(imagePath, cv2.IMREAD_UNCHANGED)
        objectImages.append(imageFull)
    return (objectImages, imageNames)

# Returns specified image from the specified directory, which is supposed to be
# used as background to put objects on. If needed, the background is cropped
# to indicated region (containing only the box with the objects).
def getImageBackground(backgroundDir, BACKGROUND_FILENAME, DO_CROP_BOX):
    backgroundPath = backgroundDir + "/" + BACKGROUND_FILENAME
    if not isfile(backgroundPath):
        print("Error: no such file " + backgroundPath)
        return np.zeros((0, 0, 3), np.uint8)

    imageBackground = cv2.imread(backgroundPath, cv2.IMREAD_UNCHANGED)
    dictBoxBorders = readConfigSection(BACKGROUND_DIR, BACKGROUND_FILENAME)

    boxTop = np.int(dictBoxBorders["top"])
    boxBottom = np.int(dictBoxBorders["bottom"])
    boxLeft = np.int(dictBoxBorders["left"])
    boxRight = np.int(dictBoxBorders["right"])
    imageBox = imageBackground[boxTop:boxBottom, boxLeft:boxRight, :]
    return imageBox

# Adds new dictionary to the list of dictioanries. Each of the dictionaries in
# the list contains information about borders of a square.
def addSquareToList(top, bottom, left, right, listSquares):
    listSquares.append({"top" : top, 
        "bottom" : bottom,
        "left" : left,
        "right" : right })

# Returns array of boolean values of indicated size, where some random of the
# elements are set to true, and the rest are false. Maximal number of true
# values is equal to MAX_OBJECTS_COUNT. The function is supposed to be used for
# random selection of object which will be put into an image.
def decideTakenImages(numImages):
    isImageTaken = [False] * numImages
    for i in range(MAX_OBJECTS_COUNT):
        indexTrue = random.randint(0, numImages - 1)
        isImageTaken[indexTrue] = True
    return isImageTaken

# The function randomly selects images from the list 'objectImages' and places
# them on the background of 'imageBoxCurrent' with random position and
# orientation trying to avoid intersections.
def putImagesOnBackground(imageBoxCurrent, objectImages, imageNames, imageMarkup = None):
    height, width, numChannels = imageBoxCurrent.shape
    dictObjects = {}
    listRectangles = []
    isImageTaken = decideTakenImages(len(objectImages))

    # shuffling images of the objects, so that we do not take them
    # in the same order every time
    imageIndeces = range(len(objectImages))
    shuffle(imageIndeces)

    for i in imageIndeces:
        objDesc = ObjectImageDescription()
        objDesc.imageWidth = width
        objDesc.imageHeight = height
        if not DO_DROP_OBJECTS:
            objDesc.isPresent = True
        else:
            objDesc.isPresent = isImageTaken[i]

        objectImage = objectImages[i]
        objectName = imageNames[i]
        cornersRot = []
        if objDesc.isPresent:
            objDesc.height, objDesc.width, channelsOrig = objectImage.shape

            # Rotating image of the object and checking whether the size is good
            oversizeCounter = 0
            while True:
                objDesc.angle = randint(0, 359)
                (imageRotated, cornersRot) = rotateImage(objectImage, \
                        objDesc.angle / 180.0 * math.pi)
                objHeight, objWidth, objChannels = imageRotated.shape
                if objHeight > height or objWidth > width:
                    oversizeCounter += 1
                    if oversizeCounter >= OVERSIZE_COUNTER_LIMIT:
                        print "Warning: object does not fit into the box"
                        objDesc.isPresent = False
                        break
                else:
                    break

            # Selecting position for rotated object, and checking that there is
            # no intersection with the other objects
            if objDesc.isPresent:
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
                        if intersectCounter >= INTERSECT_COUNTER_LIMIT:
                            print "Warning: object intersects the other objects"
                            objDesc.isPresent = False
                            break
 
            # Once the object is rotated and its position is selected, we put it
            # onto the image
            if objDesc.isPresent:
                objDesc.x = (objDesc.xBeg + objDesc.xEnd) / 2.0
                objDesc.y = (objDesc.yBeg + objDesc.yEnd) / 2.0

                putObjectOnBackground(imageBoxCurrent, imageRotated, \
                    [objDesc.xBeg, objDesc.yBeg, objDesc.xEnd, objDesc.yEnd], i + 1, imageMarkup)

        dictObjects[objectName] = objDesc.getDictionary(cornersRot)
 
    return dictObjects

# If final images are downscaled (becuase NN does not need full-scale image to
# perform detection) then coordinates of objects in the images and information
# about the images also changes, so the function applies those changes to the
# dictionary which stores the information.
def scaleCoordinates(dictObjects, factor):
    for key in dictObjects:
        dictObjects[key]["x"] = round(dictObjects[key]["x"] * factor)
        dictObjects[key]["y"] = round(dictObjects[key]["y"] * factor)
        dictObjects[key]["height"] = round(dictObjects[key]["height"] * factor)
        dictObjects[key]["width"] = round(dictObjects[key]["width"] * factor)
        dictObjects[key]["x_beg"] = round(dictObjects[key]["x_beg"] * factor)
        dictObjects[key]["y_beg"] = round(dictObjects[key]["y_beg"] * factor)
        dictObjects[key]["x_end"] = round(dictObjects[key]["x_end"] * factor)
        dictObjects[key]["y_end"] = round(dictObjects[key]["y_end"] * factor)


# Randomly changes brightness of the image
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

#timeBeginning = time.time()

imageBox = getImageBackground(BACKGROUND_DIR, BACKGROUND_FILENAME, DO_CROP_BOX)
boxHeight, boxWidth, boxChannels = imageBox.shape
objectImages, imageNames = getObjectImages(OBJECTS_DIR)
dictColors = generateDictColors(len(imageNames))
stringTime = strftime("%Y%m%d_%H%M%S", gmtime())
dirnameOutputFull = DIRNAME_OUTPUT + "/" + stringTime + "/" + DIRNAME_OUT_IMAGES
dirnameMarkupFull = DIRNAME_OUTPUT + "/" + stringTime + "/" + DIRNAME_OUT_MARKUP

subprocess.call(["mkdir", "-p", dirnameOutputFull])
subprocess.call(["mkdir", "-p", dirnameMarkupFull])

if DO_WRITE_LOG_FILE:
    logFilePath = DIRNAME_OUTPUT + "/" + stringTime + "/log.txt"
    logFile = open(logFilePath, "w")

descPictures = {}
for i in range(SAMPLE_SET_SIZE):
    imageBoxCurrent = imageBox.copy()
    imageMarkupCurrent = np.zeros((boxHeight, boxWidth), np.uint8) if DO_WRITE_MARKUP else None
    dictObjects = putImagesOnBackground(imageBoxCurrent, objectImages, imageNames, imageMarkupCurrent)
    if RESCALE_COEF != 1.0:
        imageBoxCurrent = cv2.resize(imageBoxCurrent, (0, 0), fx = RESCALE_COEF, fy = RESCALE_COEF)
        if DO_WRITE_MARKUP:
            imageMarkupCurrent = cv2.resize(imageMarkupCurrent, (0, 0), fx = RESCALE_COEF, fy = rescaleCoef)
        scaleCoordinates(dictObjects, RESCALE_COEF)
    if DO_VARIATE_BRIGHTNESS:
        imageBoxCurrent = variateBrightness(imageBoxCurrent)
    imageBoxCurrent = cv2.GaussianBlur(imageBoxCurrent, (3, 3), 0)

    outImageName = str(i) + ".png"
    outImagePath = dirnameOutputFull + "/" + outImageName
    cv2.imwrite(outImagePath, imageBoxCurrent)
    if DO_WRITE_MARKUP:
        imageMarkupColor = grayToRgb(imageMarkupCurrent, dictColors)
        #outMarkupPath = dirnameMarkupFull + "/" + outImageName
        #cv2.imwrite(outMarkupPath, imageMarkupColor)
        cv2.imwrite(outMarkupPath, imageMarkupCurrent)

    descPictures[outImageName] = dictObjects
 
    if DO_WRITE_LOG_FILE:
        logFile.write(outImageName + "\r\n")
        for objectName in dictObjects:
            if dictObjects[objectName]["is_present"] == 1.0:
                logFile.write("\t" + objectName + "\r\n")
                logFile.write("\tleft: " + str(dictObjects[objectName]["x_beg"]) + "\r\n")
                logFile.write("\ttop: " + str(dictObjects[objectName]["y_beg"]) + "\r\n")
                logFile.write("\tright: " + str(dictObjects[objectName]["x_end"]) + "\r\n")
                logFile.write("\tbottom: " + str(dictObjects[objectName]["y_end"]) + "\r\n\r\n")

        logFile.write("\r\n")
        logFile.write(" ")

writeConfigFile(dirnameOutputFull, descPictures)
if DO_WRITE_MARKUP:
    writtenDict = {}
    writtenDict["colors"] = {}
    for key in dictColors:
        currentObjectName = splitext(imageNames[key])[0]
        writtenDict["colors"][currentObjectName] = dictColors[key]
    writeConfigFile(dirnameMarkupFull, writtenDict)

if DO_WRITE_LOG_FILE:
    logFile.close()
