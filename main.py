# import cProfile
import cv2

from src.models.board import DRAW
from src.ocr.board_recognition import find_cards_on_board
from src.ocr.board_recognition import get_board_from_on_image
from src.ocr.card_recognition import find_ids_of_cards
from src.ocr.card_recognition import generate_embeddings_for_all_existing_cards
from src.simulate_game import play_algorithm_negamax
from src.simulate_game import play_algorithm_random
from src.simulate_game import simulate_game_from_start
from src.utils.display import show_image
from src.utils.display import stack_images_horizontal
from src.utils.display import stack_images_vertical
from src.utils.download_cards import CARDS_IMAGES__DEFAULT_PATH
from src.utils.download_cards import download_and_save_new_cards

"""
TODOS:
    - Move assets files around and cleanup image vs test folders
    - Simplify algorithm to find where the board is (binary search instead of 100 iterations)
    - Find position of center square of board
    - Apply algorithm from screen capture feed
"""

if __name__ == "__main__":  # noqa: C901 - complex main function during dev is fine
    # TODO() Command line params
    should_download_new_cards = False
    should_simulate_game = False
    should_try_recognize_card = True
    should_try_recognize_board = False

    if should_download_new_cards:
        download_and_save_new_cards()
        generate_embeddings_for_all_existing_cards()

    if should_simulate_game:
        statistics = {"DRAW": 0, "RED": 0, "BLUE": 0}

        while should_simulate_game:
            board = simulate_game_from_start(
                first_player_algorithm=play_algorithm_random,
                second_player_algorithm=play_algorithm_negamax,
            )

            if board.get_winner():
                statistics[board.get_winner().name] += 1
            else:
                statistics[DRAW] += 1

            print(statistics)

    if should_try_recognize_board:
        for board_number in range(11, 16):
            board_img = cv2.imread(f"assets/test_images/board/board_{board_number}.png")

            board_crop = get_board_from_on_image(board_img)
            cards_trim, matched_ids = find_cards_on_board(board_crop)
            card_images = []
            for matched_id in matched_ids:
                card_images.append(
                    cv2.imread(f"{CARDS_IMAGES__DEFAULT_PATH}{matched_id}.png")
                )

            card_trim_with_matched_card = []
            for i in range(len(card_images)):
                new_match_image = stack_images_vertical([card_images[i], cards_trim[i]])
                card_trim_with_matched_card.append(new_match_image)

            to_stack_vertical = [board_crop]
            to_stack_vertical.extend(card_trim_with_matched_card)
            board_with_matches = stack_images_horizontal(to_stack_vertical)

            final_image = stack_images_vertical([board_img, board_with_matches])
            show_image(final_image)

    if should_try_recognize_card:
        for test_card_id in range(1, 10):
            test_card_image = cv2.imread(f"assets/test_images/card/{test_card_id}.png")
            matched_cards_id = find_ids_of_cards([test_card_image])
            matched_card_from_id = cv2.imread(
                f"{CARDS_IMAGES__DEFAULT_PATH}{matched_cards_id[0]}.png"
            )
            test_image_next_to_matched_card = stack_images_horizontal(
                [test_card_image, matched_card_from_id]
            )
            show_image(test_image_next_to_matched_card)
