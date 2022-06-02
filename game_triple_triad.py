from dataclasses import dataclass
from enum import Enum
import cv2
import numpy as np

BLUE = '\033[94m'
RED = '\033[31m'
DEFAULT = '\033[0m'

HEIGHT = 128
WIDTH = 104
CHANNELS = 3


class Player(Enum):
    RED = 1
    BLUE = 2


class Modes(Enum):
    PLUS = 'PLUS'
    SAME = 'SAME'
    REVERSE = 'REVERSE'
    FALLEN_ACE = 'FALLEN_ACE'
    ASCENSION = 'ASCENSION'
    DESCENSION = 'DESCENSION'


@dataclass
class Card:
    top: int
    left: int
    right: int
    bottom: int
    id: int


class Board:
    board = [[], [], []]
    current_player = None,

    def __init__(self, first_player, modes):
        self.board = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ]
        self.current_player = first_player
        self.modes = modes

    def play(self, card, pos_x, pos_y):
        if self.board[pos_x][pos_y] is None:
            self.board[pos_x][pos_y] = {'card': card, 'color': self.current_player.name}
            neighbors = self.check_if_there_is_any_neighbors(pos_x, pos_y)
            if any(neighbors.values()):
                self.maybe_update_neighbors(card, neighbors)

            self.current_player = Player.RED if self.current_player == Player.BLUE else Player.BLUE

        else:
            raise Exception(f"This cell is already taken by another card")

    def check_if_there_is_any_neighbors(self, pos_x, pos_y):
        neighbors = {}

        if pos_x > 0:
            neighbors['top'] = self.board[pos_x - 1][pos_y]

        if pos_x < 2:
            neighbors['bottom'] = self.board[pos_x + 1][pos_y]

        if pos_y > 0:
            neighbors['left'] = self.board[pos_x][pos_y - 1]

        if pos_y < 2:
            neighbors['right'] = self.board[pos_x][pos_y + 1]

        return neighbors

    def maybe_update_neighbors(self, card, neighbors):
        for neighbor_position in neighbors:
            neighbor_card = neighbors[neighbor_position]
            self.maybe_swap_neighbor_color(card, neighbor_position, neighbor_card)

    def maybe_swap_neighbor_color(self, card, neighbor_position, neighbor_card):
        if neighbor_card is None:
            return

        if neighbor_card['color'] == self.current_player.name:
            return

        card_value = 0
        neighbor_card_value = 0

        if neighbor_position == 'top':
            card_value = card.top
            neighbor_card_value = neighbor_card['card'].bottom
        elif neighbor_position == 'left':
            card_value = card.left
            neighbor_card_value = neighbor_card['card'].right
        elif neighbor_position == 'right':
            card_value = card.right
            neighbor_card_value = neighbor_card['card'].left
        elif neighbor_position == 'bottom':
            card_value = card.bottom
            neighbor_card_value = neighbor_card['card'].top

        if self.compare(card_value, neighbor_card_value):
            neighbor_card['color'] = self.current_player.name

    def compare(self, card_1_value, card_2_value):
        if Modes.REVERSE in self.modes:
            return card_1_value < card_2_value

        if Modes.FALLEN_ACE in self.modes:
            if card_1_value == 1 and card_2_value == 10:
                return True

        return card_1_value > card_2_value

    def print(self):
        print(f" _______________________ ")
        for row in self.board:
            for card in row:
                if card:
                    top = 'A' if card['card'].top == 10 else card['card'].top
                    color = BLUE if card['color'] == Player.BLUE.name else RED
                    print(f"| {' '} {color}{top} {' '} {DEFAULT}", end='')
                else:
                    print(f"|       ", end='')

            print('|')

            for card in row:
                if card:
                    left = 'A' if card['card'].left == 10 else card['card'].left
                    right = 'A' if card['card'].right == 10 else card['card'].right
                    color = BLUE if card['color'] == Player.BLUE.name else RED
                    print(f"| {color}{left} {' '} {right} {DEFAULT}", end='')
                else:
                    print(f"|       ", end='')

            print('|')

            for card in row:
                if card:
                    bottom = 'A' if card['card'].bottom == 10 else card['card'].bottom
                    color = BLUE if card['color'] == Player.BLUE.name else RED
                    print(f"|_{'_'}_{color}{bottom}{DEFAULT}_{'_'}_", end='')
                else:
                    print(f"|_______", end='')

            print('|')

    def display(self):
        background = np.zeros((HEIGHT*3, WIDTH*3, CHANNELS), np.uint8)
        for height, row in enumerate(self.board):
            for width, cell in enumerate(row):
                if cell:
                    card_image = cv2.imread(f"assets/images/{cell['card'].id}.png")

                    if cell['color'] == Player.BLUE.name:
                        card_image = np.power(card_image, [1.3, 1.0, 1.0])
                    else:
                        card_image = np.power(card_image, [1.0, 1.0, 1.3])

                    background[height*HEIGHT:(height+1)*HEIGHT, width*WIDTH:(width+1)*WIDTH] = card_image

        cv2.imshow("", background)
        cv2.waitKey(1000)
