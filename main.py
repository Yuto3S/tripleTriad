# import cProfile
import json
import random
from random import randint

from game_triple_triad import Board
from game_triple_triad import Card
from game_triple_triad import PlayerColor
from solve_game import negamax
from solve_game import Player

# from game_triple_triad import Modes


def load_cards():
    with open("assets/cards.json") as cards_json:
        cards = json.load(cards_json)

    return cards


def simulate_game():
    board = Board(first_player=PlayerColor.BLUE, modes=[], save_history=True)

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
        print(
            "================================================================================"
        )
        for entry in board.get_history()["cards_played"]:
            print(entry)
            print(
                "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
            )

        board.print()
        # for board in board.get_history()["boards"]:
        #     print(board)
        # print(board.get_history())
        # board.print()

    print(board.get_winner())
    board.display()


def setup_board_and_players(cards):
    board = Board(first_player=PlayerColor.BLUE, modes=[], save_history=True)
    player_blue_cards = []
    player_red_cards = []

    for player_cards in [player_red_cards, player_blue_cards]:
        for i in range(0, 5):
            card_to_play = cards["cards"][randint(0, 340)]

            player_cards.append(
                Card(
                    top=card_to_play["stats"]["top"],
                    left=card_to_play["stats"]["left"],
                    right=card_to_play["stats"]["right"],
                    bottom=card_to_play["stats"]["bottom"],
                    id=card_to_play["id"],
                    type=card_to_play["type"],
                )
            )

    player_blue = Player(color=PlayerColor.BLUE, cards=player_blue_cards)
    player_red = Player(color=PlayerColor.RED, cards=player_red_cards)

    return board, player_blue, player_red


def negamax_replay(board, player_blue, player_red):
    print(player_blue)
    print(player_red)
    for i in range(9):
        if i % 2:
            random.shuffle(player_red["cards"])
            card = player_red["cards"].pop()
            positions = board.get_available_positions()
            random.shuffle(positions)
            board.play_turn(card, *positions[0])
            # _, history = negamax(board, player_red, player_red, -100, 100, 3, -1)
            # # print(value)
            # board.play_turn(history["cards_played"][i][0], *history["cards_played"][i][1])
            # player_red["cards"] = [card for card in player_red["cards"] if card != history["cards_played"][i][0]]
        else:
            _, history = negamax(board, player_blue, player_red, -100, 100, 7, 1)
            # print(value)
            board.play_turn(
                history["cards_played"][i][0], *history["cards_played"][i][1]
            )
            player_blue["cards"] = [
                card
                for card in player_blue["cards"]
                if card != history["cards_played"][i][0]
            ]

        board.print()

    print(board.get_winner())


if __name__ == "__main__":
    cards = load_cards()
    while True:
        board, player_blue, player_red = setup_board_and_players(cards)
        #
        # while True:
        # simulate_game()
        # cProfile.run("dfs(board, player_blue, player_red)")
        # cProfile.run("minmax(board, player_blue, player_red)")
        # cProfile.run("negamax_replay(board, player_blue, player_red)")
        negamax_replay(board, player_blue, player_red)
    #     cProfile.run("simulate_game")

    # cProfile.run("simulate_game()")

    # board.display()
