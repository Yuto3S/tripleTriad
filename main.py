import random
from random import randint

from game_triple_triad import Board, Card, Player, Modes
import json


def load_cards():
    with open('assets/cards.json') as cards_json:
        cards = json.load(cards_json)

    return cards


if __name__ == '__main__':
    cards = load_cards()
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
        card_to_play = randint(0, 340)
        card_in_play = cards['cards'][card_to_play]['stats']

        card = Card(
            top=card_in_play['top'],
            left=card_in_play['left'],
            right=card_in_play['right'],
            bottom=card_in_play['bottom'],
            id=cards['cards'][card_to_play]['id'],
        )
        pos = positions.pop()
        board.play(card, pos[0], pos[1])
        board.print()
        board.display()

    # board.display()
