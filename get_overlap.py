import numpy as np

def getOverlap(background_image, object_image, x_beg, y_beg, x_end, y_end):
    count_nonzero_back = np.count_nonzero(background_image)
    count_nonzero_image = np.count_nonzero(object_image)
    background_clone = background_image.copy()

    background_area = background_clone[y_beg:y_end, x_beg:x_end]
    background_area[:, :] = object_image[:, :]

    count_nonzero_joint = np.count_nonzero(background_clone)
    overlap = count_nonzero_back + count_nonzero_image - count_nonzero_joint
    overlap = 0 if overlap < 0 else overlap

    return overlap
