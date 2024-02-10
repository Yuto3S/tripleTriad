# import cProfile
import cv2
import numpy as np

from src.models.board import DRAW
from src.ocr.board_recognition import test_board_recognition
from src.ocr.card_recognition import test_one_to_many
from src.simulate_game import play_algorithm_negamax
from src.simulate_game import play_algorithm_random
from src.simulate_game import simulate_game_from_start
from src.utils.download_cards import download_and_save_new_cards


def get_one_image(images):
    img_list = []
    padding = 200
    for img in images:
        img_list.append(cv2.imread(img))
    max_width = []
    max_height = 0
    for img in img_list:
        max_width.append(img.shape[0])
        max_height += img.shape[1]
    w = np.max(max_width)
    h = max_height + padding

    # create a new array with a size large enough to contain all the images
    final_image = np.zeros((h, w, 3), dtype=np.uint8)

    current_y = (
        0  # keep track of where your current image was last placed in the y coordinate
    )
    for image in img_list:
        # add an image to the final array and increment the y coordinate
        final_image[
            current_y : image.shape[0] + current_y, : image.shape[1], :  # noqa
        ] = image
        current_y += image.shape[0]

    return final_image


if __name__ == "__main__":
    # TODO() Command line params
    should_download_new_cards = False
    should_simulate_game = False

    if should_download_new_cards:
        download_and_save_new_cards()

    statistics = {"DRAW": 0, "RED": 0, "BLUE": 0}
    while should_simulate_game:
        board = simulate_game_from_start(
            first_player_algorithm=play_algorithm_random,
            second_player_algorithm=play_algorithm_negamax,
        )
        # board = simulate_game_from_start(
        #     first_player_algorithm=play_algorithm_negamax,
        #     second_player_algorithm=play_algorithm_random,
        # )

        if board.get_winner():
            statistics[board.get_winner().name] += 1
        else:
            statistics[DRAW] += 1

        print(statistics)

    test_board_recognition()

    for test_card_id in range(6, 10):
        result_id = test_one_to_many(test_card_id)
        final_image__ = get_one_image(
            [f"assets/test_images/{test_card_id}.png", f"assets/images/{result_id}.png"]
        )
        cv2.imshow("", final_image__)
        cv2.waitKey(0)
