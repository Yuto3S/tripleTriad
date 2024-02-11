# import cProfile
import cv2

from src.models.board import DRAW
from src.ocr.board_recognition import get_board_from_on_image
from src.ocr.board_recognition import get_cards_from_board
from src.ocr.card_recognition import test_one_to_many
from src.simulate_game import play_algorithm_negamax
from src.simulate_game import play_algorithm_random
from src.simulate_game import simulate_game_from_start
from src.utils.display import get_one_image_from_images
from src.utils.display import show_image
from src.utils.download_cards import download_and_save_new_cards


if __name__ == "__main__":
    # TODO() Command line params
    should_download_new_cards = False
    should_simulate_game = False
    should_try_recognize_card = False
    should_try_recognize_board = False

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

    if should_try_recognize_board:
        for board_number in range(13, 15):
            board_img = cv2.imread(f"assets/test_images/board_{board_number}.png")

            board_trim = get_board_from_on_image(board_img)
            final_board_with_cards = get_cards_from_board(board_trim)
            final_image_to_show = get_one_image_from_images(
                [board_img, final_board_with_cards]
            )
            show_image(final_image_to_show)

    if should_try_recognize_card:
        for test_card_id in range(6, 10):
            result_id = test_one_to_many(test_card_id)
            final_image__ = get_one_image_from_images(
                [
                    f"assets/test_images/{test_card_id}.png",
                    f"assets/images/{result_id}.png",
                ]
            )
            show_image(final_image__)
