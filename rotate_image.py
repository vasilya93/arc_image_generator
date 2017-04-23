#!/usr/bin/python
import numpy as np
import cv2
import math

# The function returns image rotated for the specified angle (in radians).
# It also returns coordinates of the pixels representing coordinates of the
# corners of the initial image with respect to the center of the image.
def rotateImage(image, angle):
    rotMat = np.array([[math.cos(-angle), -math.sin(-angle)], [math.sin(-angle), math.cos(-angle)]])
    height, width, num_channels = image.shape

    corners = []
    corners.append(np.array([-width / 2.0, -height / 2.0]))
    corners.append(np.array([width / 2.0, -height / 2.0]))
    corners.append(np.array([-width / 2.0, height / 2.0]))
    corners.append(np.array([width / 2.0, height / 2.0]))

    cornersRot = []
    for corner in corners:
        cornersRot.append(rotMat.dot(corner))

    xMax = -float("Inf")
    yMax = -float("Inf")
    xMin = float("Inf")
    yMin = float("Inf")
    for corner in cornersRot:
        if corner[0] > xMax:
            xMax = corner[0]
        if corner[0] < xMin:
            xMin = corner[0]
        if corner[1] > yMax:
            yMax = corner[1]
        if corner[1] < yMin:
            yMin = corner[1]
 
    xRange = np.int(math.ceil(xMax - xMin))
    yRange = np.int(math.ceil(yMax - yMin))
    widthNew = max([width, xRange])
    heightNew = max([height, yRange])
 
    center_new = (widthNew / 2, heightNew / 2)
    offsetX = (widthNew - width) / 2
    offsetY = (heightNew - height) / 2
    imageRotated = np.zeros((heightNew, widthNew, num_channels), dtype = np.uint8)
    imageRotated[offsetY:offsetY + height, offsetX:offsetX + width, :] = image[:, :, :]

    rotMat = cv2.getRotationMatrix2D(center_new, angle / math.pi * 180, 1.0)
    imageRotated = cv2.warpAffine(imageRotated, rotMat, (widthNew, heightNew))
 
    offsetX = (widthNew - xRange) / 2
    offsetY = (heightNew - yRange) / 2
    imageRotated = imageRotated[offsetY:offsetY + yRange, offsetX:offsetX + xRange, :]

    return (imageRotated, cornersRot)
