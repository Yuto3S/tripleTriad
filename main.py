# import cProfile
import json
import random
from random import randint

from game_triple_triad import Board
from game_triple_triad import Card
from game_triple_triad import Player

# from game_triple_triad import Modes


def load_cards():
    with open("assets/cards.json") as cards_json:
        cards = json.load(cards_json)

    return cards


def simulate_game():
    board = Board(first_player=Player.BLUE, modes=[])

    positions = [
        [0, 0],
        [0, 1],
        [0, 2],
        [1, 0],
        [1, 1],
        [1, 2],
        [2, 0],
        [2, 1],
        [2, 2],
    ]
    random.shuffle(positions)

    for i in range(0, 9):
        card_to_play = cards["cards"][randint(0, 340)]

        card = Card(
            top=card_to_play["stats"]["top"],
            left=card_to_play["stats"]["left"],
            right=card_to_play["stats"]["right"],
            bottom=card_to_play["stats"]["bottom"],
            id=card_to_play["id"],
            type=card_to_play["type"],
        )
        pos = positions.pop()
        board.play_turn(card, pos[0], pos[1])
        # board.print()

    print(board.get_winner())
    board.display()


if __name__ == "__main__":
    cards = load_cards()
    #
    # while True:
    simulate_game()
    #     cProfile.run("simulate_game")

    # cProfile.run("simulate_game()")

    # board.display()
