# import cProfile
from src.models.board import DRAW
from src.simulate_game import play_algorithm_negamax
from src.simulate_game import play_algorithm_random
from src.simulate_game import simulate_game_from_start
from src.utils.download_cards import download_and_save_new_cards

if __name__ == "__main__":
    # TODO() Command line params
    if False:
        download_and_save_new_cards()

    statistics = {"DRAW": 0, "RED": 0, "BLUE": 0}
    while True:
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
