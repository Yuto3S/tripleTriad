from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np

BLUE = "\033[94m"
RED = "\033[31m"
DEFAULT = "\033[0m"

HEIGHT = 128
WIDTH = 104
CHANNELS = 3


class Player(Enum):
    RED = 1
    BLUE = 2


class Modes(Enum):
    PLUS = "PLUS"
    SAME = "SAME"
    REVERSE = "REVERSE"
    FALLEN_ACE = "FALLEN_ACE"
    ASCENSION = "ASCENSION"
    DESCENSION = "DESCENSION"


@dataclass
class Card:
    top: int
    left: int
    right: int
    bottom: int
    id: int
    type: int


class Board:
    def __init__(self, first_player, modes):
        self.board = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ]
        self.current_player = first_player
        self.modes = modes
        self.types_updated = {}

    def play_turn(self, card, pos_x, pos_y):
        if self.board[pos_x][pos_y] is None:
            for i in range(0, self.types_updated.get(card.type, 0)):
                self.update_card_values(card)

            self.play_card(card, pos_x, pos_y)

            neighbors = self.check_if_there_is_any_neighbors(pos_x, pos_y)
            self.maybe_rules_multiple_takes(neighbors, card)
            self.end_turn(card)
        else:
            raise Exception("This cell is already taken by another card")

    def play_card(self, card, pos_x, pos_y):
        self.board[pos_x][pos_y] = {"card": card, "color": self.current_player.name}
        neighbors = self.check_if_there_is_any_neighbors(pos_x, pos_y)
        if neighbors:
            self.maybe_take_over_neighbors(card, neighbors)

    def maybe_rules_multiple_takes(self, neighbors, card):
        if cell_top := neighbors.get("top"):
            if cell_left := neighbors.get("left"):
                if self.compare_rule(
                    card.top,
                    cell_top["card"].bottom,
                    card.left,
                    cell_left["card"].right,
                ):
                    self.maybe_update_cell_take_over_rule(cell_top)
                    self.maybe_update_cell_take_over_rule(cell_left)

            if cell_right := neighbors.get("right"):
                if self.compare_rule(
                    card.top,
                    cell_top["card"].bottom,
                    card.right,
                    cell_right["card"].left,
                ):
                    self.maybe_update_cell_take_over_rule(cell_top)
                    self.maybe_update_cell_take_over_rule(cell_right)

            if cell_bottom := neighbors.get("bottom"):
                if self.compare_rule(
                    card.top,
                    cell_top["card"].bottom,
                    card.bottom,
                    cell_bottom["card"].top,
                ):
                    self.maybe_update_cell_take_over_rule(cell_top)
                    self.maybe_update_cell_take_over_rule(cell_bottom)

        if cell_left := neighbors.get("left"):
            if cell_right := neighbors.get("right"):
                if self.compare_rule(
                    card.left,
                    cell_left["card"].right,
                    card.right,
                    cell_right["card"].left,
                ):
                    self.maybe_update_cell_take_over_rule(cell_left)
                    self.maybe_update_cell_take_over_rule(cell_right)

            if cell_bottom := neighbors.get("bottom"):
                if self.compare_rule(
                    card.left,
                    cell_left["card"].right,
                    card.bottom,
                    cell_bottom["card"].top,
                ):
                    self.maybe_update_cell_take_over_rule(cell_left)
                    self.maybe_update_cell_take_over_rule(cell_bottom)

        if cell_right := neighbors.get("right"):
            if cell_bottom := neighbors.get("bottom"):
                if self.compare_rule(
                    card.right,
                    cell_right["card"].left,
                    card.bottom,
                    cell_bottom["card"].top,
                ):
                    self.maybe_update_cell_take_over_rule(cell_right)
                    self.maybe_update_cell_take_over_rule(cell_bottom)

    def maybe_update_cell_take_over_rule(self, cell):
        if cell["color"] == self.current_player.name:
            return

        self.display()
        pos_x, pos_y = self.find_card_position(cell["card"].id)
        self.play_card(cell["card"], pos_x, pos_y)
        self.display()

    def end_turn(self, card):
        self.current_player = (
            Player.RED if self.current_player == Player.BLUE else Player.BLUE
        )
        self.maybe_update_card_values(card.type)

    def check_if_there_is_any_neighbors(self, pos_x, pos_y):
        neighbors = {}

        if pos_x > 0:
            if top_neighbor := self.board[pos_x - 1][pos_y]:
                neighbors["top"] = top_neighbor

        if pos_x < 2:
            if bottom_neighbor := self.board[pos_x + 1][pos_y]:
                neighbors["bottom"] = bottom_neighbor

        if pos_y > 0:
            if left_neighbor := self.board[pos_x][pos_y - 1]:
                neighbors["left"] = left_neighbor

        if pos_y < 2:
            if right_neighbor := self.board[pos_x][pos_y + 1]:
                neighbors["right"] = right_neighbor

        return neighbors

    def maybe_take_over_neighbors(self, card, neighbors):
        for neighbor_position in neighbors:
            neighbor_card = neighbors[neighbor_position]
            self.maybe_take_over_neighbor(card, neighbor_position, neighbor_card)

    def maybe_take_over_neighbor(self, card, neighbor_position, neighbor_card):
        if neighbor_card is None:
            return

        if neighbor_card["color"] == self.current_player.name:
            return

        card_value = 0
        neighbor_card_value = 0

        if neighbor_position == "top":
            card_value = card.top
            neighbor_card_value = neighbor_card["card"].bottom
        elif neighbor_position == "left":
            card_value = card.left
            neighbor_card_value = neighbor_card["card"].right
        elif neighbor_position == "right":
            card_value = card.right
            neighbor_card_value = neighbor_card["card"].left
        elif neighbor_position == "bottom":
            card_value = card.bottom
            neighbor_card_value = neighbor_card["card"].top

        if self.compare(card_value, neighbor_card_value):
            neighbor_card["color"] = self.current_player.name

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

        if Modes.SAME in self.modes:
            return card1_value1 == card2_value and card1_value2 == card3_value

    def maybe_update_card_values(self, card_type):
        if card_type == 0:
            return

        if not (Modes.ASCENSION in self.modes or Modes.DESCENSION in self.modes):
            return

        for row in self.board:
            for cell in row:
                if cell:
                    card = cell["card"]
                    if card.type == card_type:
                        self.update_card_values(card)

        self.types_updated[card_type] = self.types_updated.get(card_type, 0) + 1

    def update_card_values(self, card):
        if Modes.ASCENSION in self.modes:
            card.top = min(10, card.top + 1)
            card.left = min(10, card.left + 1)
            card.right = min(10, card.right + 1)
            card.bottom = min(10, card.bottom + 1)
        elif Modes.DESCENSION in self.modes:
            card.top = max(1, card.top - 1)
            card.left = max(1, card.left - 1)
            card.right = max(1, card.right - 1)
            card.bottom = max(1, card.bottom - 1)

    def find_card_position(self, card_id):
        for pos_x, row in enumerate(self.board):
            for pos_y, cell in enumerate(row):
                if cell and cell["card"].id == card_id:
                    return pos_x, pos_y

    def print(self):
        print(f" _______________________ ")
        for row in self.board:
            for card in row:
                if card:
                    top = "A" if card["card"].top == 10 else card["card"].top
                    color = BLUE if card["color"] == Player.BLUE.name else RED
                    print(f"| {' '} {color}{top} {' '} {DEFAULT}", end="")
                else:
                    print(f"|       ", end="")

            print("|")

            for card in row:
                if card:
                    left = "A" if card["card"].left == 10 else card["card"].left
                    right = "A" if card["card"].right == 10 else card["card"].right
                    color = BLUE if card["color"] == Player.BLUE.name else RED
                    print(f"| {color}{left} {' '} {right} {DEFAULT}", end="")
                else:
                    print(f"|       ", end="")

            print("|")

            for card in row:
                if card:
                    bottom = "A" if card["card"].bottom == 10 else card["card"].bottom
                    color = BLUE if card["color"] == Player.BLUE.name else RED
                    print(f"|_{'_'}_{color}{bottom}{DEFAULT}_{'_'}_", end="")
                else:
                    print(f"|_______", end="")

            print("|")

    def display(self):
        background = np.zeros((HEIGHT * 3, WIDTH * 3, CHANNELS), np.uint8)
        for height, row in enumerate(self.board):
            for width, cell in enumerate(row):
                if cell:
                    card_image = cv2.imread(f"assets/images/{cell['card'].id}.png")

                    if cell["color"] == Player.BLUE.name:
                        card_image = np.power(card_image, [1.3, 1.0, 1.0])
                    else:
                        card_image = np.power(card_image, [1.0, 1.0, 1.3])

                    background[
                        height * HEIGHT : (height + 1) * HEIGHT,
                        width * WIDTH : (width + 1) * WIDTH,
                    ] = card_image

        cv2.imshow("", background)
        cv2.waitKey(1000)
