import cv2
import random

import numpy as np

# Randomly changes brightness of the image
def variateBrightness(img):
    incr = random.randint(-30, 30)
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
