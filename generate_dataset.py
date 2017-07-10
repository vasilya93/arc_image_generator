#!/usr/bin/python
import numpy as np
import cv2
import os
from os import listdir
from os.path import isfile, isdir, join, splitext
from spyderlib.widgets.externalshell.introspection import LOG_FILENAME



IMAGE_DIRECTORIES="output"
LOG_FILENAMES="log.txt"
OUTPUT_FILE_NAME="dataset_list.txt"
OUTPUT_FILE_DESCR="dataset_descrp.txt"

def generateDataset():
    dirnames = [d for d in listdir(IMAGE_DIRECTORIES) if isdir(join(IMAGE_DIRECTORIES, d))]
    print dirnames
    # walking on the directory
    c=0
    output_file=open(os.path.join(IMAGE_DIRECTORIES,OUTPUT_FILE_NAME), "w")
    output_descr=open(os.path.join(IMAGE_DIRECTORIES,OUTPUT_FILE_DESCR), "w")
    for dirname in dirnames:
        #load file txt
        logfilename=os.path.join(IMAGE_DIRECTORIES,dirname,LOG_FILENAMES)
        print logfilename
        file = open(logfilename, "r")
        
        current_file=""
        filesnames=[]
        objects_by_files=dict()
        objects=[]
       
        for line in file:
            if line.find('.png')!=-1:
                if current_file!="":
                    current_file=current_file.strip()
                    path_to_image='/'+os.path.join(dirname,"images",current_file)
                    paths=[path_to_image,'/'+os.path.join(dirname,"markup",current_file)];
                    output_file.write(' '.join(paths)+'\n')
                    output_descr.write(path_to_image+" "+" ".join(objects)+'\n')
                    
                current_file=line
                objects=[]
                filesnames.append(current_file.strip())
               
            elif line.find(':')==-1:
                
                if len(line.strip())>0:
                    objects.append(line.strip())
                  
            c+=1
            
            
        #return data
        file.close()
        c+=1
        print c
    output_file.close()
    output_descr.close()

if __name__== "__main__":
    print generateDataset()