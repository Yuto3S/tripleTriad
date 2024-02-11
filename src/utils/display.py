import cv2
import numpy as np


def show_image(image):
    cv2.imshow("", image)
    cv2.waitKey(0)


def get_one_image_from_images(images):
    padding = 5

    max_width = []
    max_height = 0
    for img in images:
        max_width.append(img.shape[1])
        max_height += img.shape[0]
    w = np.max(max_width)
    h = max_height + padding

    # create a new array with a size large enough to contain all the images
    final_image = np.zeros((h, w, 3), dtype=np.uint8)

    current_y = (
        0  # keep track of where your current image was last placed in the y coordinate
    )
    for image in images:
        # add an image to the final array and increment the y coordinate
        final_image[
            current_y : image.shape[0] + current_y, : image.shape[1], :  # noqa
        ] = image
        current_y += image.shape[0]

    return final_image


def get_one_image_from_images_vertical(images):
    padding = 5

    max_width = 0
    max_height = []
    for img in images:
        max_width += img.shape[1]
        max_height.append(img.shape[0])

    w = max_width + padding
    h = np.max(max_height)

    # create a new array with a size large enough to contain all the images
    final_image = np.zeros((h, w, 3), dtype=np.uint8)

    current_x = (
        0  # keep track of where your current image was last placed in the y coordinate
    )
    for image in images:
        final_image[: image.shape[0], current_x : image.shape[1] + current_x] = image
        current_x += image.shape[1]

        # add an image to the final array and increment the y coordinate
        # final_image[
        # current_y: image.shape[0] + current_y, : image.shape[1], :  # noqa
        # ] = image
        # current_y += image.shape[0]

    return final_image
