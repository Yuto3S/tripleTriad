import random

from src.models.board import Board
from src.models.board import Player
from src.models.board import PlayerColor
from src.models.card import Card
from src.solver import negamax
from src.utils.cards_json import load_cards_stars


def simulate_game_from_start(first_player_algorithm, second_player_algorithm):
    # TODO(): We assume that BLUE always does the first move
    # Verify how it is in the game
    # I think that the player is always BLUE but the opponent can start (RED start)
    board, player_blue, player_red = setup_board_and_players()
    for i in range(9):
        if not i % 2:
            first_player_algorithm(
                board=board, player=player_blue, other_player=player_red
            )
        else:
            second_player_algorithm(
                board=board, player=player_blue, other_player=player_red
            )

        board.print()

    board.print()
    print(f"BLUE cards: {board.count_cards(PlayerColor.BLUE)}")
    print(f"RED cards: {board.count_cards(PlayerColor.RED)}")
    print(f"Winner: {board.get_winner()}")

    return board


def setup_board_and_players():
    board = Board(first_player=PlayerColor.BLUE, modes=[], save_history=True)
    player_blue = Player(
        color=PlayerColor.BLUE, cards=create_good_cards(), cards_played=[]
    )
    player_red = Player(
        color=PlayerColor.RED, cards=create_good_cards(), cards_played=[]
    )

    return board, player_blue, player_red


def create_good_cards():
    # Good cards in this context means 3 3 stars, 1 4 star and 1 5 star.
    player_cards = []

    five_stars = load_cards_stars(5)["cards"]
    four_stars = load_cards_stars(4)["cards"]
    three_stars = load_cards_stars(3)["cards"]

    good_cards = [
        random.choice(five_stars),
        random.choice(four_stars),
        random.choice(three_stars),
        random.choice(three_stars),
        random.choice(three_stars),
    ]

    for card in good_cards:
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

    return player_cards


def play_algorithm_random(board, player, **kwargs):
    random.shuffle(player["cards"])
    card = player["cards"].pop()
    positions = board.get_available_positions()
    random.shuffle(positions)
    board.play_turn(card, positions[0] // 3, positions[0] % 3)
    player["cards_played"].append(card)


def play_algorithm_negamax(board, player, other_player, **kwargs):
    current_player_color = board.get_current_player()
    if player["color"] == current_player_color:
        current_player = player
        negamax_color = -1
    else:
        current_player = other_player
        negamax_color = 1

    heuristic, best_move = negamax(
        board, other_player, player, -10000, 10000, negamax_color
    )

    if best_move is None:
        raise Exception(f"best_move None, heuristic {heuristic} to implement solution")
        # TODO Implement solution if no best_move found
        # best_move is None happens when the best heuristic is -10000 and the algorithm assumes a loss on perfect plays.
        # We need to implement some custom logic to do a "decent" move (where a card is played and protected)
        # Similarly to what is done in estimate_best_move_empty_board()

    print(
        f"Heuristic {current_player['color']} win value is: {heuristic}\n"
        f"Recommended play: \n"
        f" _____                     ______\n"
        f"|  {best_move.card.top}  |  in position      |"
        f"{'X' if best_move.position == 0 else '_'}|"
        f"{'X' if best_move.position == 1 else '_'}|"
        f"{'X' if best_move.position == 2 else '_'}|\n"
        f"|{best_move.card.left}   {best_move.card.right}|                   "
        f"|{'X' if best_move.position == 3 else '_'}|"
        f"{'X' if best_move.position == 4 else '_'}|"
        f"{'X' if best_move.position == 5 else '_'}|\n"
        f"|__{best_move.card.bottom}__|                   "
        f"|{'X' if best_move.position == 6 else '_'}|"
        f"{'X' if best_move.position == 7 else '_'}|"
        f"{'X' if best_move.position == 8 else '_'}|\n"
    )
    board.play_turn(best_move.card, best_move.position // 3, best_move.position % 3)

    current_player["cards"] = [
        card
        for card in current_player["cards"]
        if card.card_id != best_move.card.card_id
    ]

    current_player["cards_played"].append(best_move.card)
