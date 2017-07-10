#!/usr/bin/python
import numpy as np
import cv2
import os
from os import listdir
from os.path import isfile, isdir, join, splitext
from spyderlib.widgets.externalshell.introspection import LOG_FILENAME



IMAGE_DIRECTORIES="output"
DATASET_LIST="dataset_list.txt"



def getStadistics():
    path=os.path.join(IMAGE_DIRECTORIES,DATASET_LIST)
    dataset= open(path, "r")
    c=1
    bm=0
    gm=0
    rm=0
    images_sizes=dict()
    for line in dataset:
        img_paths=line.split(' ')
        #print"output"+img_paths[0]
        img=cv2.imread(IMAGE_DIRECTORIES+img_paths[0],cv2.IMREAD_UNCHANGED)
        b,g,r = cv2.split(img)
        bm=bm+(np.average(b)-bm)/c
        gm=gm+(np.average(g)-gm)/c
        rm=rm+(np.average(r)-rm)/c
        c+=1
        if not img.shape in images_sizes:
            images_sizes[img.shape]=0
        else:
            images_sizes[img.shape]+=1
        print c
        #print bm,gm,rm,images_sizes
    
    res="Number of images in the dataset "+str(c)+'\n'
    res+="Channel R mean "+str(rm)+'\n'
    res+="Channel G mean "+str(gm)+'\n'
    res+="Channel B mean "+str(bm)+'\n'
    print "Image sizes"
    print images_sizes
    return res
    
if __name__== "__main__":
    print getStadistics()