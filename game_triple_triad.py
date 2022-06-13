from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np

BLUE = "\033[94m"
RED = "\033[31m"
DEFAULT = "\033[0m"

DRAW = "DRAW"

HEIGHT = 128
WIDTH = 104
CHANNELS = 3


class PlayerColor(Enum):
    RED = 1
    BLUE = 2


class Modes(Enum):
    PLUS = "PLUS"
    SAME = "SAME"
    REVERSE = "REVERSE"
    FALLEN_ACE = "FALLEN_ACE"
    ASCENSION = "ASCENSION"
    DESCENSION = "DESCENSION"
    SUDDEN_DEATH = "SUDDEN_DEATH"  # Not implemented
    RANDOM = "RANDOM"  # Not Implemented
    ORDER = "ORDER"  # Not Implemented
    CHAOS = "CHAOS"  # Not Implemented
    SWAP = "SWAP"  # Not Implemented
    DRAFT = "DRAFT"  # Not Implemented


class Card:
    top: int
    left: int
    right: int
    bottom: int
    card_id: int
    card_type: int
    game_id: str

    def __init__(self, top, left, right, bottom, card_id, card_type, game_id=None):
        self.top = top
        self.left = left
        self.right = right
        self.bottom = bottom
        self.card_id = card_id
        self.card_type = card_type
        self.game_id = game_id

    @classmethod
    def from_card(cls, existing_card):
        return cls(
            existing_card.top,
            existing_card.left,
            existing_card.right,
            existing_card.bottom,
            existing_card.card_id,
            existing_card.card_type,
            existing_card.game_id,
        )

    def update_game_id(self, color):
        if self.game_id:
            return

        self.game_id = f"{self.card_id}{color}"

    def ascend(self):
        self.top = min(10, self.top + 1)
        self.bottom = min(10, self.bottom + 1)
        self.left = min(10, self.left + 1)
        self.right = min(10, self.right + 1)

    def descend(self):
        self.top = max(1, self.top - 1)
        self.bottom = max(1, self.bottom - 1)
        self.left = max(1, self.left - 1)
        self.right = max(1, self.right - 1)

    def get_direction(self, direction):
        match direction:
            case "top":
                return self.top
            case "bottom":
                return self.bottom
            case "left":
                return self.left
            case "right":
                return self.right

        raise Exception(f"Could not match '{direction}' to any direction")

    def get_opposite_direction(self, direction):
        match direction:
            case "top":
                return self.bottom
            case "bottom":
                return self.top
            case "left":
                return self.right
            case "right":
                return self.left

        raise Exception(f"Could not match '{direction}' to any direction")


class History(dict):
    first_player: PlayerColor
    boards = []


@dataclass
class Cell:
    card: Card
    color: PlayerColor


class Board:
    def __init__(self, first_player, modes, save_history=False):
        self.board = [None, None, None, None, None, None, None, None, None]
        self.first_player = first_player
        self.current_player = first_player
        self.modes = modes
        self.types_updated = {}
        self.winner = None
        self.save_history = save_history
        self.history = History(
            first_player=first_player,
            boards=[],
        )

    def play_turn(self, card, pos_x, pos_y):
        if self.board[int(pos_x * 3 + pos_y)] is None:
            if self.save_history:
                self.update_history()

            card.update_game_id(self.get_current_player().name)
            for i in range(0, self.types_updated.get(card.card_type, 0)):
                self.update_card_values(card)

            # PLUS and SAME should be done before regular plays
            neighbors = self.check_if_there_is_any_neighbors(pos_x, pos_y)
            self.maybe_rules_multiple_takes(neighbors, card)

            self._play_card(card, pos_x, pos_y, neighbors)

            self.end_turn(card)
        else:
            print(f"{pos_x}, {pos_x}, {card}")
            print(self.board)
            self.print()
            raise Exception("This cell is already taken by another card")

    def get_available_positions(self):
        available_positions = []
        for pos in range(0, 9):
            if self.board[pos] is None:
                available_positions.append(pos)

        return available_positions

    def _play_card(self, card, pos_x, pos_y, neighbors):
        self.board[int(pos_x * 3 + pos_y)] = Cell(card=card, color=self.current_player)
        self.maybe_take_over_neighbors(card, neighbors)

    def maybe_rules_multiple_takes(self, neighbors, card):
        if not (Modes.PLUS in self.modes or Modes.SAME in self.modes):
            return
        """
         _______________________
        |       |       |       |
        |   A   |   B   |   C   |
        |_______|_______|_______|
        |       |       |       |
        |   E   |   F   |   G   |
        |_______|_______|_______|
        |       |       |       |
        |   H   |   I   |   J   |
        |_______|_______|_______|

         If F is the card being played, we need to make 6 comparisons for all the adjacent possibilities:
            - BF & EF
            - BF & FG
            - BF & FI
            - EF & FG
            - EF & FI
            - FG & FI

        The all_comparisons list below represent those possibilities
        """
        all_comparisons = [
            {
                "neighbor1": "top",
                "neighbor2": "left",
                "neighbor1_comparison": "bottom",
                "neighbor2_comparison": "right",
            },
            {
                "neighbor1": "top",
                "neighbor2": "right",
                "neighbor1_comparison": "bottom",
                "neighbor2_comparison": "left",
            },
            {
                "neighbor1": "top",
                "neighbor2": "bottom",
                "neighbor1_comparison": "bottom",
                "neighbor2_comparison": "top",
            },
            {
                "neighbor1": "left",
                "neighbor2": "right",
                "neighbor1_comparison": "right",
                "neighbor2_comparison": "left",
            },
            {
                "neighbor1": "left",
                "neighbor2": "bottom",
                "neighbor1_comparison": "right",
                "neighbor2_comparison": "top",
            },
            {
                "neighbor1": "right",
                "neighbor2": "bottom",
                "neighbor1_comparison": "left",
                "neighbor2_comparison": "top",
            },
        ]

        for comparison in all_comparisons:
            if cell_1 := neighbors.get(comparison["neighbor1"]):
                if cell_2 := neighbors.get(comparison["neighbor2"]):
                    if self.compare_rule(
                        card.get_direction(comparison["neighbor1"]),
                        cell_1.card.get_opposite_direction(comparison["neighbor1"]),
                        card.get_direction(comparison["neighbor2"]),
                        cell_2.card.get_opposite_direction(comparison["neighbor2"]),
                    ):
                        self.maybe_update_cell_take_over_rule(cell_1)
                        self.maybe_update_cell_take_over_rule(cell_2)

    def maybe_update_cell_take_over_rule(self, cell):
        if cell.color == self.current_player:
            return

        pos_x, pos_y = self.find_card_position(cell.card.game_id)
        neighbors = self.check_if_there_is_any_neighbors(pos_x, pos_y)
        self._play_card(cell.card, pos_x, pos_y, neighbors)

    def end_turn(self, card):
        self.switch_current_player()

        if all(self.board):
            self.winner = self.calculate_winner()
        else:
            self.maybe_update_card_values(card.card_type)

    def get_winner(self):
        return self.winner

    def get_first_player(self):
        return self.first_player

    def calculate_winner(self):
        cards_to_first_player = 0
        for cell in self.board:
            if cell.color == self.first_player:
                cards_to_first_player += 1

        if cards_to_first_player > 5:
            return self.first_player
        elif cards_to_first_player == 5:
            return None
        else:
            return (
                PlayerColor.RED
                if self.first_player == PlayerColor.BLUE
                else PlayerColor.BLUE
            )

    def update_history(self):
        tmp_board = [
            Cell(card=Card.from_card(existing_card=cell.card), color=cell.color)
            if cell
            else None
            for cell in self.board
        ]
        self.history["boards"].append(tmp_board)

    def switch_current_player(self):
        self.current_player = (
            PlayerColor.BLUE
            if self.current_player == PlayerColor.RED
            else PlayerColor.RED
        )

    def undo_move(self):
        self.board = self.history["boards"].pop()
        self.switch_current_player()

    def get_history(self):
        return self.history

    def get_board(self):
        return self.board

    def get_modes(self):
        return self.modes

    def check_if_there_is_any_neighbors(self, pos_x, pos_y):
        neighbors = {}

        if pos_x > 0:
            if top_neighbor := self.board[int((pos_x - 1) * 3 + pos_y)]:
                neighbors["top"] = top_neighbor

        if pos_x < 2:
            if bottom_neighbor := self.board[int((pos_x + 1) * 3 + pos_y)]:
                neighbors["bottom"] = bottom_neighbor

        if pos_y > 0:
            if left_neighbor := self.board[int(pos_x * 3 + pos_y - 1)]:
                neighbors["left"] = left_neighbor

        if pos_y < 2:
            if right_neighbor := self.board[int(pos_x * 3 + pos_y + 1)]:
                neighbors["right"] = right_neighbor

        return neighbors

    def maybe_take_over_neighbors(self, card, neighbors):
        for neighbor_position in neighbors:
            neighbor_card = neighbors[neighbor_position]
            self.maybe_take_over_neighbor(card, neighbor_position, neighbor_card)

    def maybe_take_over_neighbor(self, card, neighbor_position, neighbor_cell):
        if neighbor_cell.color == self.current_player:
            return

        card_value = 0
        neighbor_card_value = 0

        match neighbor_position:
            case "top":
                card_value = card.top
                neighbor_card_value = neighbor_cell.card.bottom
            case "left":
                card_value = card.left
                neighbor_card_value = neighbor_cell.card.right
            case "right":
                card_value = card.right
                neighbor_card_value = neighbor_cell.card.left
            case "bottom":
                card_value = card.bottom
                neighbor_card_value = neighbor_cell.card.top

        if self.compare(card_value, neighbor_card_value):
            neighbor_cell.color = self.current_player

    def compare(self, card_1_value, card_2_value):
        if Modes.REVERSE in self.modes:
            return card_1_value < card_2_value

        if Modes.FALLEN_ACE in self.modes:
            if card_1_value == 1 and card_2_value == 10:
                return True

        return card_1_value > card_2_value

    def compare_rule(self, card1_value1, card2_value, card1_value2, card3_value):
        if Modes.PLUS in self.modes:
            return card1_value1 + card2_value == card1_value2 + card3_value
        elif Modes.SAME in self.modes:
            return card1_value1 == card2_value and card1_value2 == card3_value

    def maybe_update_card_values(self, card_type):
        if card_type == 0:
            return

        if not (Modes.ASCENSION in self.modes or Modes.DESCENSION in self.modes):
            return

        for cell in self.board:
            if cell:
                card = cell.card
                if card.card_type == card_type:
                    self.update_card_values(card)

        self.types_updated[card_type] = self.types_updated.get(card_type, 0) + 1

    def update_card_values(self, card):
        if Modes.ASCENSION in self.modes:
            card.ascend()
        elif Modes.DESCENSION in self.modes:
            card.descend()

    def find_card_position(self, card_game_id):
        for index, cell in enumerate(self.board):
            if cell:
                if cell.card.game_id == card_game_id:
                    return index // 3, index % 3

    def get_cell_information_on_position(self, pos_x, pos_y):
        return self.board[int(pos_x * 3 + pos_y)]

    def get_current_player(self):
        return self.current_player

    def print(self):
        print(" _______________________ ")
        for i in range(0, 3):
            for j in range(0, 3):
                cell = self.board[int(i * 3 + j)]
                if cell:
                    top = "A" if cell.card.top == 10 else cell.card.top
                    color = BLUE if cell.color == PlayerColor.BLUE else RED
                    print(f"| {' '} {color}{top} {' '} {DEFAULT}", end="")
                else:
                    print("|       ", end="")

            print("|")

            for j in range(0, 3):
                cell = self.board[int(i * 3 + j)]
                if cell:
                    left = "A" if cell.card.left == 10 else cell.card.left
                    right = "A" if cell.card.right == 10 else cell.card.right
                    color = BLUE if cell.color == PlayerColor.BLUE else RED
                    print(f"| {color}{left} {' '} {right} {DEFAULT}", end="")
                else:
                    print("|       ", end="")

            print("|")

            for j in range(0, 3):
                cell = self.board[int(i * 3 + j)]
                if cell:
                    bottom = "A" if cell.card.bottom == 10 else cell.card.bottom
                    color = BLUE if cell.color == PlayerColor.BLUE else RED
                    print(f"|_{'_'}_{color}{bottom}{DEFAULT}_{'_'}_", end="")
                else:
                    print("|_______", end="")

            print("|")

    def display(self):
        background = np.zeros((HEIGHT * 3, WIDTH * 3, CHANNELS), np.uint8)
        for index, cell in enumerate(self.board):
            height = index // 3
            width = index % 3

            if cell:
                card_image = cv2.imread(f"assets/images/{cell.card.card_id}.png")

                if cell.color == PlayerColor.BLUE:
                    card_image = np.power(card_image, [1.3, 1.0, 1.0])
                else:
                    card_image = np.power(card_image, [1.0, 1.0, 1.3])

                background[
                    height * HEIGHT : (height + 1) * HEIGHT,  # noqa
                    width * WIDTH : (width + 1) * WIDTH,  # noqa
                ] = card_image

        cv2.imshow("", background)
        cv2.waitKey(1000)
