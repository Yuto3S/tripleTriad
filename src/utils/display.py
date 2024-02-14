from enum import Enum

import cv2
import numpy as np


class ImageStackFormat(Enum):
    HORIZONTAL = (1, 0)
    VERTICAL = (0, 1)


def show_image(image):
    cv2.imshow("", image)
    print(
        "Please look at the image that opened in a display window. "
        "Click on any key while viewing it once you are done to move on to the next step."
    )
    cv2.waitKey(0)


def stack_images_vertical(images):
    padding = 5
    max_width = []
    max_height = 0

    for img in images:
        max_width.append(img.shape[1])
        max_height += img.shape[0]

    width = np.max(max_width)
    height = max_height + padding

    final_image = np.zeros((height, width, 3), dtype=np.uint8)

    current_y = 0
    for image in images:
        final_image[current_y : image.shape[0] + current_y, : image.shape[1] :] = image
        current_y += image.shape[0]

    return final_image


def stack_images_horizontal(images):
    padding = 5

    max_width = 0
    max_height = []
    for img in images:
        max_width += img.shape[1]
        max_height.append(img.shape[0])

    width = max_width + padding
    height = np.max(max_height)

    final_image = np.zeros((height, width, 3), dtype=np.uint8)

    current_x = 0

    for image in images:
        final_image[: image.shape[0], current_x : image.shape[1] + current_x] = image
        current_x += image.shape[1]

    return final_image
