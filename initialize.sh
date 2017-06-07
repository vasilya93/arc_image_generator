#!/bin/bash

SOURCES_DIR=sources
OBJECTS_DIR=objects
EXPO_ERASER_DIR=expo_eraser
HAND_WEIGHT_DIR=hand_weight
SPEED_STICK_DIR=speed_stick
BG_DIR=background
OUT_DIR=output

mkdir $OUT_DIR
mkdir $SOURCES_DIR

cd $SOURCES_DIR
mkdir $OBJECTS_DIR
mkdir $BG_DIR

cd $OBJECTS_DIR
mkdir $EXPO_ERASER_DIR
cd $EXPO_ERASER_DIR
wget --no-check-certificate "https://www.dropbox.com/s/gciezq481ive4jw/expo_eraser.png"
cd ..

mkdir $HAND_WEIGHT_DIR
cd $HAND_WEIGHT_DIR
wget --no-check-certificate "https://www.dropbox.com/s/dsoa55g5vayxxy8/hand_weight.png"
cd ..

mkdir $SPEED_STICK_DIR
cd $SPEED_STICK_DIR
wget --no-check-certificate "https://www.dropbox.com/s/rs8e6x95gpkillt/speed_stick.png"
cd ..

cd "../$BG_DIR"
wget --no-check-certificate "https://www.dropbox.com/s/hc45y15t327wupy/box_white.jpg"
