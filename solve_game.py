from game_triple_triad import Board
from game_triple_triad import Card
from game_triple_triad import DRAW
from game_triple_triad import PlayerColor


class Player(dict):
    color: PlayerColor
    cards: list[Card]


def endgame_heuristic(board, player):
    winner = board.get_winner()
    if winner == player["color"].name:
        return 1000, board.get_history()
    elif winner == DRAW:
        return 333, board.get_history()
    else:
        return -1000, board.get_history()


def negamax_new_and_replay(
    board, current_player, next_player, alpha, beta, depth, color
):
    if depth <= 0 or board.get_turns_played() == 9:
        value, history = endgame_heuristic(board, current_player)
        return color * value, history

    history = None
    value = -1000

    for index in range(0, len(current_player["cards"])):
        card = current_player["cards"].pop()
        for position in board.get_available_positions():
            child_board = Board(
                first_player=board.get_history()["first_player"],
                modes=[board.get_modes()],
                save_history=True,
            )
            for card_played in board.get_history()["cards_played"]:
                child_board.play_turn(card_played[0], *card_played[1])

            child_board.play_turn(card, *position)

            child_value, child_history = negamax_new_and_replay(
                child_board,
                next_player,
                current_player,
                -beta,
                -alpha,
                depth - 1,
                -color,
            )
            child_value = color * child_value
            if child_value > value:
                value = child_value
                history = child_history

            alpha = max(alpha, value)
            if alpha >= beta:
                # print(f"cut, {index}, {alpha}, {beta}, {position}")
                # current_player["cards"] = [card] + current_player["cards"]
                break

        current_player["cards"] = [card] + current_player["cards"]

    return value, history


def negamax_undo(board, current_player, next_player, alpha, beta, depth, color):
    if depth <= 0 or board.get_turns_played() == 9:
        value, history = endgame_heuristic(board, current_player)
        return color * value, history

    history = None
    value = -10000

    for index in range(0, len(current_player["cards"])):
        card = current_player["cards"].pop()
        for position in board.get_available_positions():
            board.play_turn(card, *position)
            child_value, child_history = negamax_undo(
                board,
                next_player,
                current_player,
                -beta,
                -alpha,
                depth - 1,
                -color,
            )

            child_value = color * child_value
            if child_value >= value:
                value = child_value
                # Verify if history gets updated when child_history changes
                history = child_history

            board.undo_move()

            alpha = max(alpha, value)
            if alpha >= beta:
                break

        current_player["cards"] = [card] + current_player["cards"]

    return value, history
