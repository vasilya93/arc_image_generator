#!/usr/bin/python
import numpy as np
import cv2
import os
from os import listdir
from os.path import isfile, isdir, join, splitext
from spyderlib.widgets.externalshell.introspection import LOG_FILENAME
import random
import shutil
import sys
import Image

colors = {
  'amazon-40': [
    (198,21,243), # 0=background
    (128,0,0),
    (0,128,0),
    (128,128,0),
    (0,0,128),
    (128,0,128),
    (0,128,128),
    (128,128,128),
    (64,0,0),
    (192,0,0),
    (64,128,0),
        (192,128,0),
    (64,0,128),
    (192,0,128),
    (64,128,128),
    (192,128,128),
    (0,64,0),
    (128,64,0),
    (0,192,0),
    (128,192,0),
    (0,64,128),
        (0,96,0),
    (128,96,0),
    (96,192,0),
    (128,192,96),
    (96,64,128),
        (12,96,0),
    (12,96,12),
    (24,96,12),
    (24,96,24),
    (36,108,24),
        (12,96,36),
    (48,96,12),
    (60,96,12),
    (60,96,24),
    (72,108,24),
        (60,96,36),
    (108,96,12),
    (120,96,12),
    (120,96,24)
    ]

}

def convert(filepath):
    img_mono = cv2.imread(filepath)
    if img_mono is None:
        return False
    print img_mono.shape
    dest=img_mono.copy()
    for y in range(img_mono.shape[0]):
        for x in range(img_mono.shape[1]):
            if img_mono[y,x,0]<len(colors['amazon-40']):
                dest[y,x,0]=colors['amazon-40'][img_mono[y,x,0]][2]
                dest[y,x,1]=colors['amazon-40'][img_mono[y,x,0]][1]
                dest[y,x,2]=colors['amazon-40'][img_mono[y,x,0]][0]
            else:
                dest[y,x,0]=0
                dest[y,x,1]=0
                dest[y,x,2]=0
    dir_part=filepath.split('/')
    filename_parts=dir_part[-1].split('.')
    new_filename='.'.join(["colored_"+filename_parts[0],filename_parts[1]])
    dir_part[-1]=new_filename
    new_path='/'.join(dir_part)
    cv2.imwrite(new_path,dest)
    return True
if __name__== "__main__":
    c=0
    
    for filename in sys.argv:
        if c>1:
            if convert(str(filename).strip()):
                print "Converted: ",str(filename)
            else:
                print "Fail to try to convert ",str(filename)
        c+=1
