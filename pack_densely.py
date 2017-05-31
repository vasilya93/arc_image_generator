#!/usr/bin/env python
import numpy as np
import cv2
import sys

from random import randint

BOX_HEIGHT = 480
BOX_WIDTH = 640

WINDOW_NAME = "window"


def generate_object_images():
    objects = []
    object1 = np.zeros((210, 210, 3), np.uint8)
    object1[:, :, 0] = 255
    objects.append(object1)
    object2 = np.zeros((230, 230, 3), np.uint8)
    object2[:, :, 1] = 255
    objects.append(object2)
    object3 = np.zeros((180, 180, 3), np.uint8)
    object3[:, :, 2] = 255
    objects.append(object3)
    object4 = np.zeros((175, 175, 3), np.uint8)
    object4[:, :, 1] = 127 
    object4[:, :, 2] = 255
    objects.append(object4)
    object5 = np.zeros((200, 200, 3), np.uint8)
    object5[:, :, 0] = 127 
    object5[:, :, 1] = 255
    objects.append(object5)

    return objects

def get_overlap_dispersion(background_image, object_image, x_beg, y_beg, x_end, y_end):
    count_nonzero_back = np.count_nonzero(background_image)
    count_nonzero_image = np.count_nonzero(object_image)
    background_clone = background_image.copy()

    background_area = background_clone[y_beg:y_end, x_beg:x_end]
    background_area[:, :] = object_image[:, :]

    count_nonzero_joint = np.count_nonzero(background_clone)
    overlap = count_nonzero_back + count_nonzero_image - count_nonzero_joint
    overlap = 0 if overlap < 0 else overlap

    return overlap

def get_optimal_object_position(background_image, object_image):
        height, width = object_image.shape
        if height > BOX_HEIGHT or width > BOX_WIDTH:
            print("Warning: object does not fit into the background")
            return (-1, -1)
        x_range = BOX_WIDTH - width
        y_range = BOX_HEIGHT - height

        num_samples = 10
        x_values = np.round(np.linspace(0, x_range, num_samples))
        y_values = np.round(np.linspace(0, y_range, num_samples))
        x_values = x_values.astype(int)
        y_values = y_values.astype(int)

        grid_x, grid_y = np.meshgrid(x_values, y_values)

        min_overlap = sys.maxint
        min_overlap_x = -1
        min_overlap_y = -1
        for i in range(num_samples):
            for j in range(num_samples):
                x_current = grid_x[i, j]
                y_current = grid_y[i, j]
                x_end = x_current + width
                y_end = y_current + height

                overlap = get_overlap_dispersion(background_image, object_image, \
                        x_current, y_current, x_end, y_end)
                if overlap < min_overlap:
                    min_overlap = overlap
                    min_overlap_x = x_current
                    min_overlap_y = y_current

        x_end = min_overlap_x + width
        y_end = min_overlap_y + height

        return (min_overlap_x, min_overlap_y, \
                x_end, y_end)

def get_random_object_position(background_image_gray, object_image_gray):
    height, width = object_image_gray.shape
    x_range = BOX_WIDTH - width
    y_range = BOX_HEIGHT - height
    x_beg = randint(0, x_range)
    y_beg = randint(0, y_range)
    x_end = x_beg + width
    y_end = y_beg + height
    return (x_beg, y_beg, x_end, y_end)

def put_objects_on_background(background_image, object_images):
    background_image_gray = cv2.cvtColor(background_image, cv2.COLOR_BGR2GRAY)
    for index, object_image in enumerate(object_images):
        object_image_gray = cv2.cvtColor(object_image, cv2.COLOR_BGR2GRAY)
        if index == 0:
            (x_beg, y_beg, x_end, y_end) = get_random_object_position(background_image_gray, \
                    object_image_gray) 

        else:
            (x_beg, y_beg, x_end, y_end) = get_optimal_object_position(background_image_gray, \
                    object_image_gray) 
        backgroundArea = background_image[y_beg:y_end, x_beg:x_end, :]
        backgroundArea[:, :, :] = object_image[:, :, :]
        background_image_gray = cv2.cvtColor(background_image, cv2.COLOR_BGR2GRAY)

key_code = 0

object_images = generate_object_images()
object_images.sort(key = lambda x: x.size, reverse = True)

counter = 0
while key_code != 27:
    box_image = np.zeros((BOX_HEIGHT, BOX_WIDTH, 3), np.uint8)
    put_objects_on_background(box_image, object_images)
    cv2.imshow(WINDOW_NAME, box_image)
    cv2.moveWindow(WINDOW_NAME, 100, 100)
    key_code = cv2.waitKey(0)
    cv2.imwrite(str(counter) + ".png", box_image)
    counter += 1

cv2.destroyAllWindows()
