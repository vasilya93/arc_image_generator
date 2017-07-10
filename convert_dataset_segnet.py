#!/usr/bin/python
import numpy as np
import cv2
import os
from os import listdir
from os.path import isfile, isdir, join, splitext
from spyderlib.widgets.externalshell.introspection import LOG_FILENAME
import random
import shutil

IMAGE_DIRECTORIES="/home/angeld/tensorflow-deeplab-resnet/amazon_dataset"

DATASET_TEST="test_png.txt"
DATASET_TRAIN="train_png.txt"

TRAIN_OUTPUT_DIR="raw/train"
TRAIN_LABEL_OUTPUT_DIR="raw/train-labels"
TEST_OUTPUT_DIR="raw/test"
TEST_LABEL_OUTPUT_DIR="raw/test-labels"


def doRawDataset():
    path=os.path.join(IMAGE_DIRECTORIES,DATASET_TRAIN)
    dataset= open(path, "r")
    
   
   
    c=0
    for line in dataset:
        images=line.split(' ')
        rgb_img=IMAGE_DIRECTORIES+images[0]
        lbl_img=IMAGE_DIRECTORIES+images[1]
        tmp=images[0].split('/')
        new_img_name=tmp[1].strip()+"_"+tmp[-1].strip()
       
        
        print "cp from "+ rgb_img.strip() +" to "+ os.path.join(TRAIN_OUTPUT_DIR,new_img_name)
        print "cp from "+ lbl_img.strip() +" to "+ os.path.join(TRAIN_LABEL_OUTPUT_DIR,new_img_name)

        source=cv2.imread(rgb_img.strip())
        target=cv2.resize(source,(224,224),interpolation=cv2.INTER_NEAREST)
        cv2.imwrite( os.path.join(TRAIN_OUTPUT_DIR,new_img_name),target)

        source=cv2.imread(lbl_img.strip())
        target=cv2.resize(source,(224,224),interpolation=cv2.INTER_NEAREST)
        cv2.imwrite( os.path.join(TRAIN_LABEL_OUTPUT_DIR,new_img_name),target)
        #shutil.copyfile(rgb_img.strip(),os.path.join(TRAIN_OUTPUT_DIR,new_img_name))
        #shutil.copyfile(lbl_img.strip(), os.path.join(TRAIN_LABEL_OUTPUT_DIR,new_img_name))
    
    dataset.close() 
    path=os.path.join(IMAGE_DIRECTORIES,DATASET_TEST)
    dataset= open(path, "r")
    for line in dataset:
        images=line.split(' ')
        rgb_img=IMAGE_DIRECTORIES+images[0]
        lbl_img=IMAGE_DIRECTORIES+images[1]
        tmp=images[0].split('/')
        new_img_name=tmp[1].strip()+"_"+tmp[-1].strip()
       
        
        print "cp from "+ rgb_img.strip() +" to "+ os.path.join(TEST_OUTPUT_DIR,new_img_name)
        print "cp from "+ lbl_img.strip() +" to "+ os.path.join(TEST_LABEL_OUTPUT_DIR,new_img_name)

        source=cv2.imread(rgb_img.strip())
        target=cv2.resize(source,(224,224),interpolation=cv2.INTER_NEAREST)
        cv2.imwrite( os.path.join(TEST_OUTPUT_DIR,new_img_name),target)

        source=cv2.imread(lbl_img.strip())
        target=cv2.resize(source,(224,224),interpolation=cv2.INTER_NEAREST)
        cv2.imwrite( os.path.join(TEST_LABEL_OUTPUT_DIR,new_img_name),target)
   
    dataset.close() 

    
if __name__== "__main__":
    random.seed(1234)
    doRawDataset()
    print "END"
