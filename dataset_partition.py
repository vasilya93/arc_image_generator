#!/usr/bin/python
import numpy as np
import cv2
import os
from os import listdir
from os.path import isfile, isdir, join, splitext
from spyderlib.widgets.externalshell.introspection import LOG_FILENAME
import random


IMAGE_DIRECTORIES="/home/angeld/baxter_ws/src/robinlab-arc2017-code/utilities/arc_image_generator/script/output"
DATASET_LIST="dataset_list.txt"
DATASET_SHUFFLE="dataset_random_order_png.txt"
DATASET_TEST="test_png.txt"
DATASET_TRAIN="train_png.txt"
DATASET_VALIDATE="validate_png.txt"

TRAIN_RATIO=0.8
VALIDATE_RATIO=0
TEST_RATIO=0.20


def doPartition():
    path=os.path.join(IMAGE_DIRECTORIES,DATASET_LIST)
    dataset= open(path, "r")
   
    c=0
    d0=[]
    for line in dataset:
        d0.append(line)
        c=c+1
    dataset.close() 
    
    random.shuffle(d0)
    
    dataset_test_file=open(os.path.join(IMAGE_DIRECTORIES,DATASET_TEST),'w')
    dataset_train_file=open(os.path.join(IMAGE_DIRECTORIES,DATASET_TRAIN),'w')
    dataset_val_file=open(os.path.join(IMAGE_DIRECTORIES,DATASET_VALIDATE),'w')
    
    i0=0
    i1=int(TRAIN_RATIO*len(d0))
    i2=i1+int(TEST_RATIO*len(d0))
    c=0
    for l in d0:
        if c<i1:
            dataset_train_file.write(l)
        if c>=i1 and c<i2:
            dataset_test_file.write(l)
        if c>=i2:
            dataset_val_file.write(l)
        c+=1
    dataset_test_file.close()
    dataset_train_file.close()
    dataset_val_file.close()
    
if __name__== "__main__":
    random.seed(1234)
    doPartition()
    print "END"
    