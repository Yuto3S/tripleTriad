import cv2
import numpy as np

from src.ocr.card_recognition import test_one_to_from_image
from src.utils.display import get_one_image_from_images
from src.utils.display import get_one_image_from_images_vertical

NORMALIZED_BOARD_WIDTH = 1152
NORMALIZED_BOARD_HEIGHT = 488

"""
The cards for each player are displayed in the image as shown in the following ASCII drawing:
   ______   ______   ______
  |     |  |     |  |     |
  |  1  |  |  2  |  |  3  |
  |_____|  |_____|  |_____|
       ______   ______
      |     |  |     |
      |  4  |  |  5  |
      |_____|  |_____|

The coordinates are for cards in this order and on a normalized board.
"""
CARDS_NORMALIZED_COORDINATES = [
    [(13, 176), (128, 314)],
    [(124, 176), (237, 314)],
    [(235, 176), (350, 314)],
    [(70, 320), (182, 455)],
    [(180, 320), (290, 455)],
]


# https://pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/
def get_board_from_on_image(image):
    template = cv2.imread("assets/images/board_cut.jpg")
    image_height, image_width, _ = image.shape
    template_height, template_width, _ = template.shape

    best_match = None

    # TODO(): Improve area narrowing down with a better algorithm, maybe binary search?
    for scale in np.linspace(0.5, 1.5, 100)[::-1]:
        resized_width = int(image_width * scale)
        resized_height = int(image_height * scale)
        ratio = image_width / float(resized_width)

        if resized_width < template_width or resized_height < template_height:
            break

        resized = cv2.resize(
            image, (resized_width, resized_height), interpolation=cv2.INTER_AREA
        )
        result_match_template = cv2.matchTemplate(
            resized, template, cv2.TM_CCOEFF_NORMED
        )
        _, max_value, _, max_location = cv2.minMaxLoc(result_match_template)

        if best_match is None or max_value > best_match["value"]:
            best_match = {
                "value": max_value,
                "location": max_location,
                "ratio": ratio,
            }

    board_trim_coordinates = get_board_coordinates(
        best_match, template_width, template_height
    )

    board = image[
        board_trim_coordinates["start"]["y"] : board_trim_coordinates["end"]["y"],
        board_trim_coordinates["start"]["x"] : board_trim_coordinates["end"]["x"],
    ]
    normalized_board = cv2.resize(
        board,
        (NORMALIZED_BOARD_WIDTH, NORMALIZED_BOARD_HEIGHT),
        interpolation=cv2.INTER_AREA,
    )
    return normalized_board


def get_board_coordinates(best_match, template_width, template_height):
    start_x = int(best_match["location"][0] * best_match["ratio"])
    start_y = int(best_match["location"][1] * best_match["ratio"])
    end_x = int((best_match["location"][0] + template_width) * best_match["ratio"])
    end_y = int((best_match["location"][1] + template_height) * best_match["ratio"])

    return {
        "start": {
            "x": start_x,
            "y": start_y,
        },
        "end": {
            "x": end_x,
            "y": end_y,
        },
    }


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
