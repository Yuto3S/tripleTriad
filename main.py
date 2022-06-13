import cProfile
import json
import random

from game_triple_triad import Board
from game_triple_triad import Card
from game_triple_triad import PlayerColor
from solve_game import negamax_undo
from solve_game import Player


def load_cards():
    with open("assets/cards.json") as cards_json:
        cards = json.load(cards_json)

    return cards


def load_cards_stars(stars):
    with open(f"assets/cards_{stars}.json") as cards_json:
        cards = json.load(cards_json)

    return cards


# def simulate_game():
#     board = Board(first_player=PlayerColor.BLUE, modes=[], save_history=True)
#
#     positions = [
#         [0, 0],
#         [0, 1],
#         [0, 2],
#         [1, 0],
#         [1, 1],
#         [1, 2],
#         [2, 0],
#         [2, 1],
#         [2, 2],
#     ]
#     random.shuffle(positions)
#
#     for i in range(0, 9):
#         card_to_play = cards["cards"][randint(0, 340)]
#
#         card = Card(
#             top=card_to_play["stats"]["top"],
#             left=card_to_play["stats"]["left"],
#             right=card_to_play["stats"]["right"],
#             bottom=card_to_play["stats"]["bottom"],
#             id=card_to_play["id"],
#             type=card_to_play["type"],
#         )
#         pos = positions.pop()
#         board.play_turn(card, pos[0], pos[1])
#         print(
#             "================================================================================"
#         )
#         for entry in board.get_history()["cards_played"]:
#             print(entry)
#             print(
#                 "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
#             )
#
#         board.print()
#         # for board in board.get_history()["boards"]:
#         #     print(board)
#         # print(board.get_history())
#         # board.print()
#
#     print(board.get_winner())
#     board.display()


def setup_board_and_players():
    board = Board(first_player=PlayerColor.BLUE, modes=[], save_history=True)
    player_blue_cards = []
    player_red_cards = []

    five_stars = load_cards_stars(5)["cards"]
    four_stars = load_cards_stars(4)["cards"]
    three_stars = load_cards_stars(3)["cards"]

    for player_cards in [player_red_cards, player_blue_cards]:
        tmp_cards = [
            random.choice(five_stars),
            random.choice(four_stars),
            random.choice(three_stars),
            random.choice(three_stars),
            random.choice(three_stars),
        ]

        for card in tmp_cards:
            player_cards.append(
                Card(
                    top=card["stats"]["top"],
                    left=card["stats"]["left"],
                    right=card["stats"]["right"],
                    bottom=card["stats"]["bottom"],
                    id=card["id"],
                    type=card["type"],
                )
            )

    player_blue = Player(color=PlayerColor.BLUE, cards=player_blue_cards)
    player_red = Player(color=PlayerColor.RED, cards=player_red_cards)

    return board, player_blue, player_red


def negamax_replay(board, player_blue, player_red):
    # # print(player_blue)
    # # print(player_red)
    # for i in range(9):
    #     if i % 2:
    #         random.shuffle(player_red["cards"])
    #         card = player_red["cards"].pop()
    #         positions = board.get_available_positions()
    #         random.shuffle(positions)
    #         board.play_turn(card, *positions[0])
    #         # _, history = negamax(board, player_red, player_red, -100, 100, 3, -1)
    #         # # print(value)
    #         # board.play_turn(history["cards_played"][i][0], *history["cards_played"][i][1])
    #         # player_red["cards"] = [card for card in player_red["cards"] if card != history["cards_played"][i][0]]
    #     else:
    #         heuristic, history = negamax_undo(board, player_blue, player_red, -1000, 1000, 5, 1)
    #         import ipdb; ipdb.set_trace()
    #         # print(heuristic)
    #         # print(history)
    #         # print(len(history["cards_played"]))
    #         # import ipdb; ipdb.set_trace()
    #         board.play_turn(
    #             history["cards_played"][i][0], *history["cards_played"][i][1]
    #         )
    #         # print(basic_heuristic(board, player_blue))
    #         #
    #         # child_board = Board(
    #         #     first_player=board.get_history()["first_player"],
    #         #     modes=[board.get_modes()],
    #         #     save_history=True,
    #         # )
    #         # for card in history["cards_played"]:
    #         #     child_board.play_turn(card[0], *card[1])
    #         #     child_board.print()
    #
    #         player_blue["cards"] = [
    #             card
    #             for card in player_blue["cards"]
    #             if card != history["cards_played"][i][0]
    #         ]
    #
    #     # print("============================================================")
    #     board.print()
    #
    # print(board.get_winner())
    # card_blue = player_blue["cards"].pop()
    # card_red = player_red["cards"].pop()
    # board.play_turn(card_blue, 0, 0)
    # board.play_turn(card_red, 2, 2)
    # board.play_turn(card_blue_2, 0, 2)
    # board.play_turn(card_red_2, 1, 0)
    heuristic, history = negamax_undo(
        board, player_blue, player_red, -10000, 10000, 9, 1
    )


def save_x_stars(stars, cards):
    tmp_cards = []
    for card in cards["cards"]:
        if card["stars"] == stars:
            tmp_cards.append(card)

    save_cards(stars, tmp_cards)


def save_cards(stars, cards):
    with open(f"cards_{stars}.json", "w") as cards_json:
        json.dump({"cards": cards}, cards_json)


if __name__ == "__main__":
    # cards = load_cards()
    # save_x_stars(5, cards)
    # save_x_stars(4, cards)
    # save_x_stars(3, cards)
    statistics = {"DRAW": 0, "RED": 0, "BLUE": 0}
    while True:
        board, player_blue, player_red = setup_board_and_players()
        # print(player_red)
        # print(player_blue)
        # while True:
        # simulate_game()
        # cProfile.run("dfs(board, player_blue, player_red)")
        # cProfile.run("minmax(board, player_blue, player_red)")
        # cProfile.run("negamax_replay(board, player_blue, player_red)")
        cProfile.run("negamax_replay(board, player_blue, player_red)")
        # negamax_replay(board, player_blue, player_red)
        statistics[board.get_winner()] += 1
        print(statistics)
        # except Exception:
        #     pass
    # cProfile.run("simulate_game")

    # cProfile.run("simulate_game()")

    # board.display()
