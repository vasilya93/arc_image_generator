# ARC image generator
Set of Python scripts to generate image sets for training of a neural network. Images have a view of a tray with some objects in it - something which could be used in Amazon Robotic Challenge.

# Installation
First, it is necessary to clone the repository, initialize the directory structure and download initial object images:
```
git clone https://github.com/vasilya93/arc_image_generator.git
cd arc_image_generator
./initialize.sh
```
The script *initialize.sh* will create directories *output* and *source*, and will place some initial images into the directory *source*. After this, it is necessary to run the script *set_box_borders.py* which will allow to set borders for the images placed in the directory *source/background*, so that object placement script further knows in which region of background it can place objects. Running *set_box_borders.py* will lead to windows with images from *source/background* popping up. In the images, one need to denote borders of the box. To do this, one can use keyboard buttons 'w', 'a', 's', 'd', space and left mouse button. Pressing 'w' button notifies, that upper box border now will be set, 'a' - that left border will be set, 's' - that bottom border will be set, 'd' - that left border will be set. Pressing mouse key sets selected border, which is shown in the image. Once one finished with setting borders, it is possible to space to proceed to the next background or to finish the procedure.

The script *pack_box.py* is the main part of the package - it takes object images from the directory *source/objects* and puts it on one of the background in the directory *source/background* in different poses. In the script *pack_box* there is a set of essential constants which control functioning of the script, these constant are:
* BACKGROUND_FILENAME - name of the file from the directory *source/background* which will be used as background for the objects;
* SAMPLE_SET_SIZE - number of output images generated;
* RESCALE_COEF - coefficient to rescale generated images. If it is equal to 1.0, original background and object images keep their original size;
* DO_CROP_BOX - if it is true, generated images keep only that area of background which is marked as box in configuration file (look above for instructions on *set_box_borders.py* script);
* DO_VARIATE_BRIGHTNESS - if set to True, brightness of generated images is varied, so that NN trained on the dataset can make more generalization;
DO_DROP_OBJECTS - if set to True, the script does not try to put all of the objects into the image it once - it selects MAX_OBJECTS_COUNT number of object and tries to fit them into the box;
MAX_OBJECTS_COUNT - maximal number of objects, which the script tries to fit into the image if DO_DROP_OBJECTS is set to True.

After the script *pack_box.py* is run, generated images can be found in the directory *output* in subdirectory with corresponding date and time. Apart from the images, in the directory there is a file *config.ini* with information about positions of objects in the images.
