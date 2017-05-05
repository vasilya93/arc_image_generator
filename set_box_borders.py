#!/usr/bin/python
import numpy as np
import ConfigParser
import io
import cv2

from os import listdir
from os.path import isfile, join, splitext
from config_file import writeConfigFile
from image_check import getImageNames

BACKGROUND_DIR = "sources/background"
WINDOW_NAME = "Background"

MODE_SET_TOP = 0
MODE_SET_BOTTOM = 1
MODE_SET_LEFT = 2
MODE_SET_RIGHT = 3

ProgramMode = MODE_SET_TOP
ImageOriginal = np.zeros((0, 0, 3), np.uint8)
ImageShown = np.zeros((0, 0, 3), np.uint8)

TOP = -1
BOTTOM = -1
LEFT = -1
RIGHT = -1

def drawBorders():
    global TOP, BOTTOM, LEFT, RIGHT
    global ImageShown
    ImageShown = ImageOriginal.copy()
    height, width, num_channels = ImageShown.shape
    lineWidth = 2
    if TOP != -1:
        cv2.line(ImageShown, (0, TOP), (width - 1, TOP), (255, 0, 0), lineWidth)
        cv2.line(ImageShown, (0, TOP + lineWidth), (width - 1, TOP + lineWidth), (255, 255, 255), lineWidth)
    if BOTTOM != -1:
        cv2.line(ImageShown, (0, BOTTOM), (width - 1, BOTTOM), (0, 255, 0), lineWidth)
        cv2.line(ImageShown, (0, BOTTOM - lineWidth), (width - 1, BOTTOM - lineWidth), (255, 255, 255), lineWidth)
    if LEFT != -1:
        cv2.line(ImageShown, (LEFT, 0), (LEFT, height - 1), (255, 0, 0), lineWidth)
        cv2.line(ImageShown, (LEFT + lineWidth, 0), (LEFT + lineWidth, height - 1), (255, 255, 255), lineWidth)
    if RIGHT != -1:
        cv2.line(ImageShown, (RIGHT, 0), (RIGHT, height - 1), (0, 255, 0), lineWidth)
        cv2.line(ImageShown, (RIGHT - lineWidth, 0), (RIGHT - lineWidth, height - 1), (255, 255, 255), lineWidth)

def mouseHandler(event, x, y, flags, param):
    global TOP, BOTTOM, LEFT, RIGHT
    if event == cv2.EVENT_LBUTTONDOWN:
        if ProgramMode == MODE_SET_LEFT:
            LEFT = x
        elif ProgramMode == MODE_SET_RIGHT:
            RIGHT = x
        elif ProgramMode == MODE_SET_BOTTOM:
            BOTTOM = y
        elif ProgramMode == MODE_SET_TOP:
            TOP = y
        drawBorders()

def resetBorders():
    global TOP, BOTTOM, LEFT, RIGHT
    TOP = -1
    BOTTOM = -1
    LEFT = -1
    RIGHT = -1

def changeProgramMode(keyCode):
    global ProgramMode
    doChangeImage = False
    doExit = False
    if keyCode == 27: # ESC
        doExit = True 
    elif keyCode == 32: # Space
        doChangeImage = True 
    elif keyCode == 97: # A
        ProgramMode = MODE_SET_LEFT
    elif keyCode == 100: # D
        ProgramMode = MODE_SET_RIGHT
    elif keyCode == 115: # S
        ProgramMode = MODE_SET_BOTTOM
    elif keyCode == 119: # W
        ProgramMode = MODE_SET_TOP
    return (doChangeImage, doExit)

def addImageData(imageData, imageName):
    if TOP != -1 and BOTTOM != -1 and LEFT != -1 and RIGHT != -1:
        imageData[imageName] = {}
        imageData[imageName]["top"] = TOP
        imageData[imageName]["bottom"] = BOTTOM
        imageData[imageName]["left"] = LEFT
        imageData[imageName]["right"] = RIGHT

imageData = {}
imageNames = getImageNames(BACKGROUND_DIR)
cv2.namedWindow(WINDOW_NAME)
cv2.setMouseCallback(WINDOW_NAME, mouseHandler)
for imageName in imageNames:
    resetBorders()
    imagePath = BACKGROUND_DIR + "/" + imageName
    ImageOriginal = cv2.imread(imagePath, cv2.IMREAD_UNCHANGED)
    ImageShown = ImageOriginal.copy()
    doChangeImage = False; doExit = False
    while not (doChangeImage or doExit):
        cv2.imshow(WINDOW_NAME, ImageShown)
        keyCode = cv2.waitKey(20) & 0xEFFFFF
        doChangeImage, doExit = changeProgramMode(keyCode)
    addImageData(imageData, imageName)
    if doExit:
        break
if len(imageData) != 0:
    writeConfigFile(BACKGROUND_DIR, imageData)
