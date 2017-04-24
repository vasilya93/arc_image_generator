#!/bin/bash

SOURCES_DIR=sources
OBJECTS_DIR=objects
BG_DIR=background
OUT_DIR=output

mkdir $OUT_DIR
mkdir $SOURCES_DIR

cd $SOURCES_DIR
mkdir $OBJECTS_DIR
mkdir $BG_DIR

cd $OBJECTS_DIR
wget --no-check-certificate "https://www.dropbox.com/s/gciezq481ive4jw/expo_eraser.png?dl=0"
wget --no-check-certificate "https://www.dropbox.com/s/dsoa55g5vayxxy8/hand_weight.png?dl=0"
wget --no-check-certificate "https://www.dropbox.com/s/rs8e6x95gpkillt/speed_stick.png?dl=0"

cd "../$BG_DIR"
wget --no-check-certificate "https://www.dropbox.com/s/hc45y15t327wupy/box_white.jpg?dl=0"
