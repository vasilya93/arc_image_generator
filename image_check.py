#!/usr/bin/python
from os import listdir
from os.path import isfile, isdir, join, splitext

IMAGE_EXTENSIONS = [".jpg", ".png"]

def isImageExtension(checkedExtension):
    for extension in IMAGE_EXTENSIONS:
        if extension == checkedExtension:
            return True
    return False

def getImageNames(parentDirectory):
    filenames = [f for f in listdir(parentDirectory) if isfile(join(parentDirectory, f))]
    image_names = []
    for full_name in filenames:
        filename, file_extension = splitext(full_name)
        if isImageExtension(file_extension):
            image_names.append(full_name)
    return image_names

def getDirnamesImages(parentDirectory):
    dirnames = [d for d in listdir(parentDirectory) if isdir(join(parentDirectory, d))]
    dictDirnamesImages = {}
    for dirname in dirnames:
        imageNames = getImageNames(parentDirectory + "/" + dirname)
        if len(imageNames) != 0:
            dictDirnamesImages[dirname] = imageNames
    return dictDirnamesImages
