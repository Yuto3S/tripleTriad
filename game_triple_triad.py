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

    def get_game_id(self):
        return self.game_id

    def get_type(self):
        return self.card_type


class History(dict):
    cards_played = []
    first_player: PlayerColor
    boards = []


class Cell:
    color: PlayerColor
    card: Card

    def __init__(self, card, color):
        self.card = card
        self.color = color

    def get_color(self):
        return self.color

    def get_card(self):
        return self.card


class Board:
    def __init__(self, first_player, modes, save_history=False):
        self.board = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ]
        self.first_player = first_player
        self.current_player = first_player
        self.game_ended_cards_to_first_player = 0
        self.modes = modes
        self.types_updated = {}
        self.winner = None
        self.save_history = save_history
        self.turns_played = 0
        self.history = History(
            cards_played=[],
            first_player=first_player.name,
            boards=[],
        )

    def play_turn(self, card, pos_x, pos_y):
        if self.board[pos_x][pos_y] is None:
            if self.save_history:
                self.update_history(card, pos_x, pos_y)

            card.update_game_id(self.get_current_player().name)
            for i in range(0, self.types_updated.get(card.get_type(), 0)):
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
        for pos_x, row in enumerate(self.board):
            for pos_y, cell in enumerate(row):
                if cell is None:
                    available_positions.append((pos_x, pos_y))

        return available_positions

    def _play_card(self, card, pos_x, pos_y, neighbors):
        self.board[pos_x][pos_y] = Cell(card=card, color=self.current_player)
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
                        card[comparison["neighbor1"]],
                        cell_1["card"][comparison["neighbor1_comparison"]],
                        card[comparison["neighbor2"]],
                        cell_2["card"][comparison["neighbor2_comparison"]],
                    ):
                        self.maybe_update_cell_take_over_rule(cell_1)
                        self.maybe_update_cell_take_over_rule(cell_2)

    def maybe_update_cell_take_over_rule(self, cell):
        if cell.get_color() == self.current_player:
            return

        pos_x, pos_y = self.find_card_position(cell.get_card().get_game_id())
        neighbors = self.check_if_there_is_any_neighbors(pos_x, pos_y)
        self._play_card(cell.get_card(), pos_x, pos_y, neighbors)

    def end_turn(self, card):
        self.turns_played += 1
        if self.turns_played == 9:
            self.winner = self.calculate_winner()

        self.switch_current_player()
        self.maybe_update_card_values(card.get_type())

    def get_winner(self):
        return self.winner

    def get_first_player(self):
        return self.first_player

    def get_turns_played(self):
        return self.turns_played

    def calculate_winner(self):
        cards_to_first_player = 0
        for row in self.board:
            for cell in row:
                if cell.get_color() == self.first_player:
                    cards_to_first_player += 1

        self.game_ended_cards_to_first_player = cards_to_first_player

        if cards_to_first_player > 5:
            return self.first_player.name
        elif cards_to_first_player == 5:
            return DRAW
        else:
            return (
                PlayerColor.RED.name
                if self.first_player == PlayerColor.BLUE
                else PlayerColor.BLUE.name
            )

    def update_history(self, card, pos_x, pos_y):
        self.history["cards_played"].append((card, (pos_x, pos_y)))

        tmp_board = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ]
        for pos_x, row in enumerate(self.board):
            for pos_y, cell in enumerate(row):
                if cell is not None:
                    tmp_board[pos_x][pos_y] = Cell(
                        card=Card.from_card(cell.get_card()),
                        color=cell.get_color(),
                    )

        self.history["boards"].append(tmp_board)

    def switch_current_player(self):
        self.current_player = (
            PlayerColor.BLUE
            if self.current_player == PlayerColor.RED
            else PlayerColor.RED
        )

    def undo_move(self):
        if self.turns_played <= 0:
            raise Exception("Can't undo move when no move has been registered")

        self.history["cards_played"].pop()
        self.board = self.history["boards"].pop()
        self.turns_played -= 1
        self.switch_current_player()

    def get_history(self):
        return self.history

    def get_game_ended_cards_to_first_player(self):
        return self.game_ended_cards_to_first_player

    def get_board(self):
        return self.board

    def get_modes(self):
        return self.modes

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
        if neighbor_card.get_color() == self.current_player:
            return

        card_value = 0
        neighbor_card_value = 0

        if neighbor_position == "top":
            card_value = card.top
            neighbor_card_value = neighbor_card.get_card().bottom
        elif neighbor_position == "left":
            card_value = card.left
            neighbor_card_value = neighbor_card.get_card().right
        elif neighbor_position == "right":
            card_value = card.right
            neighbor_card_value = neighbor_card.get_card().left
        elif neighbor_position == "bottom":
            card_value = card.right
            neighbor_card_value = neighbor_card.get_card().top

        if self.compare(card_value, neighbor_card_value):
            neighbor_card.color = self.current_player.name

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

        for row in self.board:
            for cell in row:
                if cell:
                    card = cell["card"]
                    if card["type"] == card_type:
                        self.update_card_values(card)

        self.types_updated[card_type] = self.types_updated.get(card_type, 0) + 1

    def update_card_values(self, card):
        values = ["top", "left", "right", "bottom"]

        if Modes.ASCENSION in self.modes:
            for value in values:
                card[value] = min(10, card[value] + 1)
        elif Modes.DESCENSION in self.modes:
            for value in values:
                card[value] = max(1, card[value] - 1)

    def find_card_position(self, card_game_id):
        for pos_x, row in enumerate(self.board):
            for pos_y, cell in enumerate(row):
                if cell:
                    if cell.get_card()["card_game_id"] == card_game_id:
                        return pos_x, pos_y

    def get_cell_information_on_position(self, pos_x, pos_y):
        return self.board[pos_x][pos_y]

    def get_current_player(self):
        return self.current_player

    def print(self):
        print(" _______________________ ")
        for row in self.board:
            for cell in row:
                if cell:
                    top = "A" if cell.get_card().top == 10 else cell.get_card().top
                    color = BLUE if cell.get_color() == PlayerColor.BLUE.name else RED
                    print(f"| {' '} {color}{top} {' '} {DEFAULT}", end="")
                else:
                    print("|       ", end="")

            print("|")

            for cell in row:
                if cell:
                    left = "A" if cell.get_card().left == 10 else cell.get_card().left
                    right = (
                        "A" if cell.get_card().right == 10 else cell.get_card().right
                    )
                    color = BLUE if cell.get_color() == PlayerColor.BLUE.name else RED
                    print(f"| {color}{left} {' '} {right} {DEFAULT}", end="")
                else:
                    print("|       ", end="")

            print("|")

            for cell in row:
                if cell:
                    bottom = (
                        "A" if cell.get_card().bottom == 10 else cell.get_card().bottom
                    )
                    color = BLUE if cell.get_color() == PlayerColor.BLUE.name else RED
                    print(f"|_{'_'}_{color}{bottom}{DEFAULT}_{'_'}_", end="")
                else:
                    print("|_______", end="")

            print("|")

    def display(self):
        background = np.zeros((HEIGHT * 3, WIDTH * 3, CHANNELS), np.uint8)
        for height, row in enumerate(self.board):
            for width, cell in enumerate(row):
                if cell:
                    card_image = cv2.imread(f"assets/images/{cell['card']['id']}.png")

                    if cell.get_color() == PlayerColor.BLUE:
                        card_image = np.power(card_image, [1.3, 1.0, 1.0])
                    else:
                        card_image = np.power(card_image, [1.0, 1.0, 1.3])

                    background[
                        height * HEIGHT : (height + 1) * HEIGHT,  # noqa
                        width * WIDTH : (width + 1) * WIDTH,  # noqa
                    ] = card_image

        cv2.imshow("", background)
        cv2.waitKey(1000)
