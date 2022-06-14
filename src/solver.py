from typing import NamedTuple
from typing import Tuple

from src.models.card import Card


CORNER_DIRECTIONS_POSITIONS = [
    ("right", "bottom", 0),
    ("left", "bottom", 2),
    ("right", "top", 6),
    ("left", "top", 8),
]


class Move(NamedTuple):
    card: Card
    position: Tuple


def endgame_heuristic(board, player):
    winner = board.get_winner()

    if winner == player["color"]:
        return 1000
    elif winner is None:  # DRAW
        return 0
    else:
        return -1000


def estimate_best_move_empty_board(current_player):
    best_move = None
    best_move_value = 0

    for card in current_player["cards"]:
        for corner in CORNER_DIRECTIONS_POSITIONS:
            if card.get_direction(corner[0]) > 8 or card.get_direction(corner[1]) > 8:
                break

            corner_value = card.get_direction(corner[0]) + card.get_direction(corner[1])
            if corner_value > best_move_value:
                best_move_value = corner_value
                best_move = Move(card=card, position=corner[2])

    print(f"estimate_best_move_empty_board {best_move}")

    return best_move


def negamax(board, current_player, next_player, alpha, beta, color):
    if any(board.get_board()):
        return negamax_undo(board, current_player, next_player, alpha, beta, color)

    best_move = estimate_best_move_empty_board(current_player)
    return 0, best_move


def negamax_undo(board, current_player, next_player, alpha, beta, color):
    heuristic = -10000
    best_move = None

    if all(board.get_board()):
        heuristic = endgame_heuristic(board, next_player)
        return color * heuristic, best_move

    for index in range(0, len(current_player["cards"])):
        card = current_player["cards"].pop()
        for position in board.get_available_positions():
            board.play_turn(card, position // 3, position % 3)
            recursive_heuristic, _ = negamax_undo(
                board,
                next_player,
                current_player,
                -beta,
                -alpha,
                -color,
            )

            recursive_heuristic = -1 * recursive_heuristic
            if recursive_heuristic > heuristic:
                heuristic = recursive_heuristic
                best_move = Move(card=card, position=position)

            board.undo_move()

            alpha = max(alpha, heuristic)
            if alpha >= beta:
                break

        current_player["cards"] = [card] + current_player["cards"]

    return heuristic, best_move
