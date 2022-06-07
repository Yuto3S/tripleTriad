from game_triple_triad import Board
from game_triple_triad import Card
from game_triple_triad import PlayerColor


class Player(dict):
    color: PlayerColor
    cards: list[Card]


def basic_heuristic(board, player):
    heuristic = 0
    for row in board.get_board():
        for cell in row:
            if cell:
                if cell["color"] == player:
                    heuristic += 1
                else:
                    heuristic -= 1

    return heuristic, board.get_history()


def negamax(board, current_player, next_player, alpha, beta, depth, color):
    if depth <= 0 or board.get_turns_played() == 9:
        value, history = basic_heuristic(board, board.get_first_player())
        return color * value, history

    history = None
    value = -100

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

            child_value, child_history = negamax(
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
                current_player["cards"] = [card] + current_player["cards"]
                return value, history

        current_player["cards"] = [card] + current_player["cards"]

    return value, history
