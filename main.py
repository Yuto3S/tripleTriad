# import cProfile
import json
import random

from game_triple_triad import Board
from game_triple_triad import Card
from game_triple_triad import DRAW
from game_triple_triad import PlayerColor
from solve_game import negamax
from solve_game import Player


def load_cards():
    with open("assets/cards.json") as cards_json:
        cards_x = json.load(cards_json)

    return cards_x


def load_cards_stars(stars):
    with open(f"assets/cards_{stars}.json") as cards_json:
        cards = json.load(cards_json)

    return cards


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
                    card_id=card["id"],
                    card_type=card["type"],
                )
            )

    player_blue = Player(
        color=PlayerColor.BLUE, cards=player_blue_cards, cards_played=[]
    )
    player_red = Player(color=PlayerColor.RED, cards=player_red_cards, cards_played=[])

    return board, player_blue, player_red


def simulate_negamax_versus_random(board, player_blue, player_red):
    for i in range(9):
        if not i % 2:
            heuristic, best_move = negamax(
                board, player_blue, player_red, -10000, 10000, 1
            )

            if best_move is None:
                raise Exception("F best_move done, to implement solution")
                # TODO Implement solution if no best_move found

            print(
                f"Heuristic blue win: {heuristic} by playing {best_move.card.top} in {best_move.position}"
            )
            board.play_turn(
                best_move.card, best_move.position // 3, best_move.position % 3
            )

            player_blue["cards"] = [
                card
                for card in player_blue["cards"]
                if card.card_id != best_move.card.card_id
            ]

            player_blue["cards_played"].append(best_move.card)
        else:
            random.shuffle(player_red["cards"])
            card = player_red["cards"].pop()
            positions = board.get_available_positions()
            random.shuffle(positions)
            board.play_turn(card, positions[0] // 3, positions[0] % 3)
            player_red["cards_played"].append(card)

    print(f"Winner: {board.get_winner()}")


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
    statistics = {"DRAW": 0, "RED": 0, "BLUE": 0}
    while True:
        board, player_blue, player_red = setup_board_and_players()
        simulate_negamax_versus_random(board, player_blue, player_red)
        if board.get_winner():
            statistics[board.get_winner().name] += 1
        else:
            statistics[DRAW] += 1

        print(statistics)
