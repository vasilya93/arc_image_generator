#!/usr/bin/python
import numpy as np
import cv2
import os
from os import listdir
from os.path import isfile, isdir, join, splitext
from spyderlib.widgets.externalshell.introspection import LOG_FILENAME
import random
import Image

IMAGE_DIRECTORIES="output"
DATASET_LIST="dataset_list.txt"
DATASET_JPG_LIST="dataset_jpg_list.txt"


def doConversion():
    path=os.path.join(IMAGE_DIRECTORIES,DATASET_LIST)
    dataset= open(path, "r")
    dataset_jpg=open(os.path.join(IMAGE_DIRECTORIES,DATASET_JPG_LIST),'w')
   
    c=0
    d0=[]
    for line in dataset:
        paths=line.split(' ')
        path=paths[0];
        filename=os.path.basename(path)
        dirname=os.path.dirname(path)
        file_ext=filename.split('.')
        new_file=file_ext[0]+".jpg"
        new_path=os.path.join(dirname,new_file)
        new_line=' '.join([new_path,paths[-1]])
        print IMAGE_DIRECTORIES+path
        print IMAGE_DIRECTORIES+new_path
        #im = Image.open(os.path.join(IMAGE_DIRECTORIES,path[0]))
        #im.save(os.path.join(IMAGE_DIRECTORIES,new_path))
        print line+"--->"+new_line
        dataset_jpg.write(new_line)
        
    dataset.close()
    
    
if __name__== "__main__":
    random.seed(1234)
    doConversion()
    print "END"  