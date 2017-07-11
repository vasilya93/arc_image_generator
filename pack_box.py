#!/usr/bin/python
import numpy as np
import cv2
import math
import subprocess
import random
import os
import time
import sys
from random import randint
from time import gmtime, strftime
from os.path import isfile, splitext
from copy import deepcopy

from image_check import getImageNames, getDirnamesImages
from config_file import readConfigFile, writeConfigFile, writeSimpleConfig
from rectangle import Rectangle
from gray_to_rgb import grayToRgb, generateDictColors, generateDictGray
from get_overlap import getOverlap
from optparse import OptionParser
from variate_brightness import variateBrightness

from put_images_on_background import putImagesOnBackground
from generate_object_focused_image import generateObjectFocusedImage

# TODO: ensure that some of the objects is dropped when their total area is too big
#       (overlap is too high)

# Constants
WINDOW_NAME = "Box"

class ParamConfig:
    INTERSECT_COUNTER_LIMIT = 100
    OVERSIZE_COUNTER_LIMIT = 100
    DO_DROP_OBJECTS = True
    MAX_OBJECTS_COUNT = 5
    DO_VARIATE_BRIGHTNESS = True
    DO_RESCALE_OBJECTS = True
    OBJECT_SCALE_VARIATION = 0.3
    DO_WRITE_MARKUP = False
    IS_MARKUP_COLORED = False
    DO_PUT_DENSELY = False
    RESCALE_COEF = 1
    SAMPLE_SET_SIZE = 5
    DO_WRITE_LOG_FILE = False
    DO_SAVE_WHOLE_IMAGE = False

global param_config

# Returns list of images (of objects) and names of the images from
# the directory which is given as parameter to the function.
def getObjectImages(parentDirectory):
    dictDirnamesImageNames = getDirnamesImages(parentDirectory)
    dictObjectImages = {}
    objectNames = []
    for dirname in dictDirnamesImageNames:
        objectNames.append(dirname)
        dictObjectImages[dirname] = []
        for imageName in dictDirnamesImageNames[dirname]:
            imagePath = parentDirectory + "/" + dirname + "/" + imageName
            imageFull = cv2.imread(imagePath, cv2.IMREAD_UNCHANGED)
            dictObjectImages[dirname].append(imageFull)
    return (dictObjectImages, objectNames)

# Returns specified image from the specified directory, which is supposed to be
# used as background to put objects on. If needed, the background is cropped
# to indicated region (containing only the box with the objects).
def getImagesBackground(backgroundDir):
    imageNames = getImageNames(backgroundDir)
    dictBoxBorders = readConfigFile(backgroundDir)
    backgroundImages = []
    backgroundFullImages = []
    for filename in imageNames:
        imagePath = backgroundDir + "/" + filename
        imageFull = cv2.imread(imagePath, cv2.IMREAD_UNCHANGED)
        boxTop = np.int(dictBoxBorders[filename]["top"])
        boxBottom = np.int(dictBoxBorders[filename]["bottom"])
        boxLeft = np.int(dictBoxBorders[filename]["left"])
        boxRight = np.int(dictBoxBorders[filename]["right"])
        imageBox = imageFull[boxTop:boxBottom, boxLeft:boxRight, :]
        backgroundImages.append(imageBox)
        backgroundFullImages.append(imageFull)
    if len(backgroundImages) != 0:
        backgroundImages.sort(key = lambda x: x.shape[0])
        minHeight = backgroundImages[0].shape[0]
        backgroundImages.sort(key = lambda x: x.shape[1])
        minWidth = backgroundImages[0].shape[1]
        for index, image in enumerate(backgroundImages):
            height, width, channels = image.shape
            x_beg = (width - minWidth) / 2; x_end = x_beg + minWidth
            y_beg = (height - minHeight) / 2; y_end = y_beg + minHeight
            backgroundImages[index] = image[y_beg:y_end, x_beg:x_end, :]
    return backgroundImages, backgroundFullImages

def getDictImagesBackground(backgroundDir):
    imageNames = getImageNames(backgroundDir)
    dictBoxBorders = readConfigFile(backgroundDir)
    backgroundImages = []
    for filename in imageNames:
        imagePath = backgroundDir + "/" + filename
        imageFull = cv2.imread(imagePath, cv2.IMREAD_UNCHANGED)
        boxTop = np.int(dictBoxBorders[filename]["top"])
        boxBottom = np.int(dictBoxBorders[filename]["bottom"])
        boxLeft = np.int(dictBoxBorders[filename]["left"])
        boxRight = np.int(dictBoxBorders[filename]["right"])
        backgroundImages.append({"image": imageFull, \
                "top": boxTop, \
                "left": boxLeft, \
                "width": boxRight - boxLeft, \
                "height": boxBottom - boxTop})
    if len(backgroundImages) > 0:
        backgroundImages.sort(key = lambda x: x["height"])
        minHeight = backgroundImages[0]["height"]
        backgroundImages.sort(key = lambda x: x["width"])
        minWidth = backgroundImages[0]["width"]
        for image_desc in backgroundImages:
            height = image_desc["height"]
            width = image_desc["width"]
            image_desc["left"] += (width - minWidth) / 2
            image_desc["width"] = minWidth
            image_desc["top"] += (height - minHeight) / 2
            image_desc["height"] = minHeight
    return backgroundImages

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

def scaleBoxDimensions(boxDescription, factor):
    boxDescription["left"] = int(round(boxDescription["left"] * factor))
    boxDescription["top"] = int(round(boxDescription["top"] * factor))
    boxDescription["width"] = int(round(boxDescription["width"] * factor))
    boxDescription["height"] =  int(round(boxDescription["height"] * factor))

if __name__== "__main__":
    global param_config
    param_config=ParamConfig();
    usage="Usage: %prog [options]"
    parser=OptionParser(usage)
    parser.add_option("-o",
                      "--output_dir",
                      dest="output_dir",
                      default="output",
                      help="Output dir for storing results ")
    parser.add_option("-g",
                      "--images_out_dir",
                      dest="images_out_dir",
                      default="images",
                      help="Output dir for storing images ")
    parser.add_option("-m",
                      "--markup_out_dir",
                      dest="markup_out_dir",
                      default="markup",
                      help="Output dir for storing markups ")
    parser.add_option("-b",
                      "--background_dir",
                      dest="background_dir",
                      default="./sources/background",
                      help="Input dir with the images RGB background images ")
    parser.add_option("-j",
                      "--objects_dir",
                      dest="objects_dir",
                      default="./sources/objects",
                      help="Input dir with the images RGBA object images ")
    parser.add_option("-l",
                      "--intersect_counter_limit",
                      dest="intersect_counter_limit",
                      default=100,
                      help="unknow")
    parser.add_option("-s",
                      "--oversize_counter_limit",
                      dest="oversize_counter_limit",
                      default=100,
                      help="unknow")
    parser.add_option("-d",
                      "--do_drop_objects",
                      dest="do_drop_objects",
                      default=True,
                      help="unknow")
    parser.add_option("-c",
                      "--max_object_count",
                      dest="max_object_count",
                      default=5,
                      help="unknow")
    parser.add_option("-n",
                      "--variate_brightness",
                      dest="variate_brightness",
                      default=True,
                      help="unknow")
    parser.add_option("-a",
                      "--rescale_objects",
                      dest = "rescale_objects",
                      default = True,
                      help = "Will objects be randomly rescaled withing certain range"
                      " before being added to the background")
    parser.add_option("-t",
                      "--object_scale_variation",
                      dest = "object_scale_variation",
                      default = 0.3,
                      help = "Specifies range for possible increase and decrease in the scale of object images." 
                      "Is only applicable if <rescale_objects> is set to <True>")
    parser.add_option("-w",
                      "--write_markup",
                      dest="write_markup",
                      default=False,
                      help="unknow")
    parser.add_option("-u",
                      "--markup_colored",
                      dest="markup_colored",
                      default=False,
                      help="unknow")
    parser.add_option("-x",
                      "--put_densely",
                      dest="put_densely",
                      default=False,
                      help="unknow")
    parser.add_option("-v",
                      "--write_log",
                      dest="write_log",
                      default=False,
                      help="unknow")
    parser.add_option("-r",
                      "--rescale_coef",
                      dest="rescale_coef",
                      default=1,
                      help="unknow")
    parser.add_option("-p",
                      "--sample_set_size",
                      dest="sample_set_size",
                      default=5,
                      help="unknow")
    parser.add_option("-z",
                      "--get_object_labels",
                      dest="get_object_labels",
                      default=0,
                      help="Generate a list of labels an grey scale level and RGB id")
    parser.add_option("-i",
                      "--save_whole_image",
                      dest="save_whole_image",
                      default=False,
                      help="Do save whole generated image instead of only area marked as box")
    options,args=parser.parse_args()
 
    BACKGROUND_DIR = options.background_dir
    OBJECTS_DIR = options.objects_dir
    DIRNAME_OUT_MARKUP = options.markup_out_dir
    DIRNAME_OUT_IMAGES = options.images_out_dir
    DIRNAME_OUTPUT=options.output_dir
 
    param_config.INTERSECT_COUNTER_LIMIT = options.intersect_counter_limit
    param_config.OVERSIZE_COUNTER_LIMIT= options.oversize_counter_limit
    param_config.DO_DROP_OBJECTS = eval(options.do_drop_objects) if \
            isinstance(options.do_drop_objects, basestring) else \
            options.do_drop_objects
    param_config.MAX_OBJECTS_COUNT = int(options.max_object_count)
    param_config.DO_VARIATE_BRIGHTNESS = eval(options.variate_brightness) if \
            isinstance(options.variate_brightness, basestring) else \
            options.variate_brightness
    param_config.DO_RESCALE_OBJECTS = bool(options.rescale_objects)
    param_config.OBJECT_SCALE_VARIATION = float(options.object_scale_variation)
    param_config.DO_WRITE_MARKUP = bool(options.write_markup)
    param_config.IS_MARKUP_COLORED = eval(options.markup_colored) if \
            isinstance(options.markup_colored, basestring) else \
            options.markup_colored
    param_config.DO_PUT_DENSELY = eval(options.put_densely) if \
            isinstance(options.put_densely, basestring) else \
            options.put_densely
    param_config.DO_WRITE_LOG_FILE = eval(options.write_log) if \
            isinstance(options.write_log, basestring) else \
            options.write_log
    param_config.RESCALE_COEF = float(options.rescale_coef)
    param_config.SAMPLE_SET_SIZE = int(options.sample_set_size)
    param_config.DO_SAVE_WHOLE_IMAGE = bool(options.save_whole_image)

    if param_config.OBJECT_SCALE_VARIATION >= 1 or param_config.OBJECT_SCALE_VARIATION < 0:
        print("Warning: value %f of <object_scale_variation> is out of the range [0; 1), "
                "no scale variation will be performed." % param_config.OBJECT_SCALE_VARIATION)
        param_config.DO_RESCALE_OBJECTS = False
        param_config.OBJECT_SCALE_VARIATION = 0.0

    logFile = None
    backgroundImages = getDictImagesBackground(BACKGROUND_DIR)
    numBackgroundImages = len(backgroundImages)
    if numBackgroundImages == 0:
        print("Error: no background images were found. Exiting...")
        exit(1)
 
    imageBox = backgroundImages[0]
    bgHeight, bgWidth, _ = imageBox["image"].shape
 
    dictObjectImages, objectNames = getObjectImages(OBJECTS_DIR)
    dictColors = generateDictColors(len(objectNames))
 
    if options.get_object_labels:
        writtenDict = generateDictGray(objectNames)
        print writtenDict
        print "-----------------"
        print dictColors
        exit(0)

    stringTime = strftime("%Y%m%d_%H%M%S", gmtime())
    dirnameOutputFull = DIRNAME_OUTPUT + "/" + stringTime + "/" + DIRNAME_OUT_IMAGES
    dirnameMarkupFull = DIRNAME_OUTPUT + "/" + stringTime + "/" + DIRNAME_OUT_MARKUP
 
    subprocess.call(["mkdir", "-p", dirnameOutputFull])
    subprocess.call(["mkdir", "-p", dirnameMarkupFull])
 
    if param_config.DO_WRITE_LOG_FILE:
        logFilePath = DIRNAME_OUTPUT + "/" + stringTime + "/log.txt"
        logFile = open(logFilePath, "w")
 
    descPictures = {}
    timeBeginning = time.time()
    for i in range(param_config.SAMPLE_SET_SIZE):
        backgroundIndex = randint(0, numBackgroundImages - 1)
        imageDictCurrent = deepcopy(backgroundImages[backgroundIndex])
        topCurrent = imageDictCurrent["top"]
        leftCurrent = imageDictCurrent["left"]
        heightCurrent = imageDictCurrent["height"]
        widthCurrent = imageDictCurrent["width"]
        backgroundFullCurrent = imageDictCurrent["image"]
        imageBoxCurrent = backgroundFullCurrent[topCurrent:topCurrent + heightCurrent, \
                leftCurrent:leftCurrent + widthCurrent, :]
        # there is a problem with this copy, as it is not attached to 
        #backgroundFullCurrent = backgroundFullImages[backgroundIndex]
 
        dictObjectImagesCopy = deepcopy(dictObjectImages)
        imageMarkupCurrent = None
        if param_config.DO_WRITE_MARKUP or param_config.DO_PUT_DENSELY:
            imageMarkupFullCurrent = np.zeros((bgHeight, bgWidth), np.uint8)
            imageMarkupCurrent = imageMarkupFullCurrent[topCurrent:topCurrent + heightCurrent, \
                leftCurrent:leftCurrent + widthCurrent]

        dictObjects = putImagesOnBackground(imageBoxCurrent, dictObjectImages, objectNames, param_config, imageMarkupCurrent)

        if param_config.RESCALE_COEF != 1.0:
            backgroundFullCurrent = cv2.resize(backgroundFullCurrent, (0, 0), fx = param_config.RESCALE_COEF, fy = param_config.RESCALE_COEF)
            if param_config.DO_WRITE_MARKUP:
                imageMarkupFullCurrent = cv2.resize(imageMarkupFullCurrent, (0, 0), fx = param_config.RESCALE_COEF, fy = param_config.RESCALE_COEF)
            scaleCoordinates(dictObjects, param_config.RESCALE_COEF)
            scaleBoxDimensions(imageDictCurrent, param_config.RESCALE_COEF)
        if param_config.DO_VARIATE_BRIGHTNESS:
            backgroundFullCurrent = variateBrightness(backgroundFullCurrent)
        backgroundFullCurrent = cv2.GaussianBlur(backgroundFullCurrent, (3, 3), 0)

        topCurrent = imageDictCurrent["top"]
        leftCurrent = imageDictCurrent["left"]
        heightCurrent = imageDictCurrent["height"]
        widthCurrent = imageDictCurrent["width"]
        imageBoxCurrent = backgroundFullCurrent[topCurrent:topCurrent + heightCurrent, \
                leftCurrent:leftCurrent + widthCurrent, :]
        if param_config.DO_WRITE_MARKUP:
            imageMarkupCurrent = imageMarkupFullCurrent[topCurrent:topCurrent + heightCurrent, \
                leftCurrent:leftCurrent + widthCurrent]
 
        outImageName = str(i) + ".png"
        outImagePath = dirnameOutputFull + "/" + outImageName
        outMarkupPath = dirnameMarkupFull + "/" + outImageName

        if param_config.DO_SAVE_WHOLE_IMAGE:
            cv2.imwrite(outImagePath, backgroundFullCurrent)
            if param_config.DO_WRITE_MARKUP:
                imageMarkupColor = grayToRgb(imageMarkupFullCurrent, dictColors) 
                if param_config.IS_MARKUP_COLORED:
                    cv2.imwrite(outMarkupPath, imageMarkupColor)
                else:
                    cv2.imwrite(outMarkupPath, imageMarkupFullCurrent)
        else:
            cv2.imwrite(outImagePath, imageBoxCurrent)
            if param_config.DO_WRITE_MARKUP:
                imageMarkupColor = grayToRgb(imageMarkupCurrent, dictColors) 
                if param_config.IS_MARKUP_COLORED:
                    cv2.imwrite(outMarkupPath, imageMarkupColor)
                else:
                    cv2.imwrite(outMarkupPath, imageMarkupCurrent)
 
        descPictures[outImageName] = dictObjects
 
        if param_config.DO_WRITE_LOG_FILE:
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
 
        timeCurrent = time.time()
        timeElapsed = timeCurrent - timeBeginning
        timePerImage = timeElapsed / (i + 2)
        timeLeft = (param_config.SAMPLE_SET_SIZE - 1 - i) * timePerImage
        timeLeftString = time.strftime('%H:%M:%S', time.gmtime(int(timeLeft)))
        print("%dth image is processed, estimated time left is %s" % (i + 1, timeLeftString))
 
    writeConfigFile(dirnameOutputFull, descPictures)
    if param_config.DO_WRITE_MARKUP:
        if param_config.IS_MARKUP_COLORED:
            writtenDict = {}
            writtenDict["colors"] = {}
            for key in dictColors:
                if key >= len(objectNames):
                    continue
                currentObjectName = objectNames[key]
                writtenDict["colors"][currentObjectName] = dictColors[key]
            writeConfigFile(dirnameMarkupFull, writtenDict)
        else:
            writtenDict = generateDictGray(objectNames)
            writeSimpleConfig(dirnameMarkupFull, writtenDict)
 
    if param_config.DO_WRITE_LOG_FILE:
        logFile.close()
