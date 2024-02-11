import cv2
import numpy as np

from src.ocr.card_recognition import test_one_to_from_image
from src.utils.display import get_one_image_from_images
from src.utils.display import get_one_image_from_images_vertical


"""
We are doing a normalization of the input image by scaling the board found on the picture to our reference size.
This reference size has some assumed logic built on top of it for the coordinates of each area:
    - where are the cards,
    - where is the center board,
    - where is left VS right player.

The cards for each player are displayed in the image as shown in the following ASCII drawing:
   ______   ______   ______
  |     |  |     |  |     |
  |  1  |  |  2  |  |  3  |
  |_____|  |_____|  |_____|
       ______   ______
      |     |  |     |
      |  4  |  |  5  |
      |_____|  |_____|

The following hardcoded values are all these assumed key points (x, y) used by the logic.
"""
CARDS_NORMALIZED_COORDINATES = [
    [(13, 176), (128, 314)],
    [(124, 176), (237, 314)],
    [(235, 176), (350, 314)],
    [(70, 320), (182, 455)],
    [(180, 320), (290, 455)],
]
NORMALIZED_BOARD_WIDTH = 1152
NORMALIZED_BOARD_HEIGHT = 488

BEST_MATCH_VALUE = "value"
BEST_MATCH_LOCATION = "location"
BEST_MATCH_RATIO = "ratio"

CROP_START_POINT = "start_crop_point"
CROP_END_POINT = "end_crop_point"

COORDINATE_X = "x"
COORDINATE_Y = "y"


# https://pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/
def get_board_from_on_image(image):
    board_template = cv2.imread("assets/images/board_cut.jpg")
    image_height, image_width, _ = image.shape
    template_height, template_width, _ = board_template.shape

    best_match = None

    # TODO(): Improve area narrowing down with a better algorithm, maybe binary search?
    for scale in np.linspace(0.5, 1.5, 100)[::-1]:
        better_match_found = maybe_find_better_match(
            scale, image, board_template, best_match.get(BEST_MATCH_VALUE, 0)
        )
        if better_match_found:
            best_match = {
                BEST_MATCH_VALUE: better_match_found[BEST_MATCH_VALUE],
                BEST_MATCH_LOCATION: better_match_found[BEST_MATCH_LOCATION],
                BEST_MATCH_RATIO: better_match_found[BEST_MATCH_RATIO],
            }

    crop_coordinates = get_board_crop_coordinates(
        best_match, template_width, template_height
    )
    normalized_board = crop_and_normalize_board(image, crop_coordinates)

    return normalized_board


def maybe_find_better_match(scale, image, template, current_best_match):
    image_height, image_width, _ = image.shape
    template_height, template_width, _ = template.shape
    resized_width = int(image_width * scale)
    resized_height = int(image_height * scale)
    ratio = image_width / float(resized_width)

    if resized_width < template_width or resized_height < template_height:
        return None

    resized_image = cv2.resize(
        image, (resized_width, resized_height), interpolation=cv2.INTER_AREA
    )
    result_match_template = cv2.matchTemplate(
        resized_image, template, cv2.TM_CCOEFF_NORMED
    )
    _, max_value, _, max_location = cv2.minMaxLoc(result_match_template)

    if max_value > current_best_match:
        return {
            BEST_MATCH_VALUE: max_value,
            BEST_MATCH_LOCATION: max_location,
            BEST_MATCH_RATIO: ratio,
        }

    return None


def get_board_crop_coordinates(best_match, template_width, template_height):
    crop_coordinates = {
        CROP_START_POINT: {
            COORDINATE_X: int(
                best_match[BEST_MATCH_LOCATION][0] * best_match[BEST_MATCH_RATIO]
            ),
            COORDINATE_Y: int(
                best_match[BEST_MATCH_LOCATION][1] * best_match[BEST_MATCH_RATIO]
            ),
        },
        CROP_END_POINT: {
            COORDINATE_X: int(
                (best_match[BEST_MATCH_LOCATION][0] + template_width)
                * best_match[BEST_MATCH_RATIO]
            ),
            COORDINATE_Y: int(
                (best_match[BEST_MATCH_LOCATION][1] + template_height)
                * best_match[BEST_MATCH_RATIO]
            ),
        },
    }

    return crop_coordinates


def crop_and_normalize_board(image, crop_coordinates):
    board = image[
        crop_coordinates[CROP_START_POINT][COORDINATE_Y] : crop_coordinates[
            CROP_END_POINT
        ][COORDINATE_Y],
        crop_coordinates[CROP_START_POINT][COORDINATE_X] : crop_coordinates[
            CROP_END_POINT
        ][COORDINATE_X],
    ]
    normalized_board = cv2.resize(
        board,
        (NORMALIZED_BOARD_WIDTH, NORMALIZED_BOARD_HEIGHT),
        interpolation=cv2.INTER_AREA,
    )

    return normalized_board


def get_cards_from_board(board):
    comparison_images = [board]

    for card_start, card_end in CARDS_NORMALIZED_COORDINATES:
        current_card = board[card_start[1] : card_end[1], card_start[0] : card_end[0]]
        matching_id = test_one_to_from_image(current_card)
        matched_image = cv2.imread(f"assets/images/{matching_id}.png")
        comparison_image = get_one_image_from_images([current_card, matched_image])
        comparison_images.append(comparison_image)

    final_cmp_img = get_one_image_from_images_vertical(comparison_images)
    return final_cmp_img
    # show_image(final_cmp_img)
