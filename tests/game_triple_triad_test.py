import copy

import pytest

from game_triple_triad import Board
from game_triple_triad import Card
from game_triple_triad import DRAW
from game_triple_triad import Modes
from game_triple_triad import Player
from tests.utils.const import HIGH_VALUE
from tests.utils.const import LOW_VALUE
from tests.utils.const import MEDIUM_VALUE

ALL_POSITIONS = [
    [0, 0],
    [0, 1],
    [0, 2],
    [1, 0],
    [1, 1],
    [1, 2],
    [2, 0],
    [2, 1],
    [2, 2],
]

SANDWICH_INFOS = (
    "card1_pos, card2_pos",
    [
        ((1, 0), (0, 1)),
        ((1, 0), (1, 2)),
        ((1, 0), (2, 1)),
        ((0, 1), (1, 2)),
        ((0, 1), (2, 1)),
        ((1, 2), (2, 1)),
    ],
)


@pytest.fixture
def low_card():
    return Card(
        top=LOW_VALUE,
        left=LOW_VALUE,
        right=LOW_VALUE,
        bottom=LOW_VALUE,
        id=0,
        type=0,
    )


@pytest.fixture
def medium_card():
    return Card(
        top=MEDIUM_VALUE,
        left=MEDIUM_VALUE,
        right=MEDIUM_VALUE,
        bottom=MEDIUM_VALUE,
        id=1,
        type=0,
    )


@pytest.fixture
def high_card():
    return Card(
        top=HIGH_VALUE,
        left=HIGH_VALUE,
        right=HIGH_VALUE,
        bottom=HIGH_VALUE,
        id=2,
        type=0,
    )


class TestBoard:
    first_player = Player.BLUE
    second_player = Player.RED

    def test_board_init(self):
        board = Board(first_player=self.first_player, modes=[])
        assert board.board == [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ]
        assert board.current_player == Player.BLUE
        assert board.modes == []

    @pytest.mark.parametrize("mode, expected", [(mode, [mode]) for mode in Modes])
    def test_assert_board_created_with_correct_modes(self, mode, expected):
        board = Board(first_player=self.first_player, modes=[mode])
        assert board.modes == expected

    def test_board_can_not_play_card_if_spot_already_taken(self, low_card, high_card):
        board = Board(first_player=self.first_player, modes=[])
        board.play_turn(low_card, 0, 0)
        with pytest.raises(Exception):
            board.play_turn(high_card, 0, 0)


class TestCardTakesOverNeighbor(TestBoard):
    @pytest.mark.parametrize(
        "card_position, second_card_position",
        [
            # Top Left
            ((0, 0), (0, 1)),
            ((0, 0), (1, 0)),
            # Top Center
            ((0, 1), (0, 0)),
            ((0, 1), (0, 2)),
            ((0, 1), (1, 1)),
            # Top Right
            ((0, 2), (0, 1)),
            ((0, 2), (1, 2)),
            # Left Middle
            ((1, 0), (0, 0)),
            ((1, 0), (1, 1)),
            ((1, 0), (2, 0)),
            # Center
            ((1, 1), (0, 1)),
            ((1, 1), (1, 0)),
            ((1, 1), (1, 2)),
            ((1, 1), (2, 1)),
            # Right Middle
            ((1, 2), (0, 2)),
            ((1, 2), (1, 1)),
            ((1, 2), (2, 2)),
            # Bottom Left
            ((2, 0), (1, 0)),
            ((2, 0), (2, 1)),
            # Bottom Center
            ((2, 1), (2, 0)),
            ((2, 1), (1, 1)),
            ((2, 1), (2, 2)),
            # Top Right
            ((2, 2), (2, 1)),
            ((2, 2), (1, 2)),
        ],
    )
    def test_takes_over_from_the_(
        self, card_position, second_card_position, low_card, high_card
    ):
        self.board = Board(first_player=self.first_player, modes=[])
        self.board.play_turn(low_card, *card_position)
        self.board.play_turn(high_card, *second_card_position)
        assert (
            self.board.get_cell_information_on_position(*card_position)["color"]
            == self.second_player
        )

    def test_takes_over_multiple_cards_at_once(self, low_card, high_card):
        self.board = Board(first_player=self.first_player, modes=[])
        blue_card_positions = [(0, 0), (0, 2)]
        self.board.play_turn(low_card, *blue_card_positions[0])
        self.board.play_turn(copy.copy(low_card), 2, 2)
        self.board.play_turn(copy.copy(low_card), *blue_card_positions[1])
        for blue_position in blue_card_positions:
            assert (
                self.board.get_cell_information_on_position(*blue_position)["color"]
                == self.first_player
            )

        self.board.play_turn(high_card, 0, 1)

        for blue_position in blue_card_positions:
            assert (
                self.board.get_cell_information_on_position(*blue_position)["color"]
                == self.second_player
            )

    def test_does_not_take_over_if_same_value(self, high_card):
        self.board = Board(first_player=self.first_player, modes=[])
        self.board.play_turn(high_card, 1, 1)
        self.board.play_turn(copy.copy(high_card), 0, 1)
        assert (
            self.board.get_cell_information_on_position(1, 1)["color"]
            == self.first_player
        )


class TestRules(TestBoard):
    def test_reverse(self, high_card, low_card):
        self.board = Board(first_player=self.first_player, modes=[Modes.REVERSE])
        self.board.play_turn(high_card, 1, 1)
        self.board.play_turn(low_card, 0, 1)

        assert (
            self.board.get_cell_information_on_position(1, 1)["color"]
            == self.second_player
        )

    def test_fallen_ace(self, high_card, low_card):
        self.board = Board(first_player=self.first_player, modes=[Modes.FALLEN_ACE])
        self.board.play_turn(high_card, 1, 1)
        self.board.play_turn(low_card, 0, 1)

        assert (
            self.board.get_cell_information_on_position(1, 1)["color"]
            == self.second_player
        )

    def test_fallen_ace_does_not_work_for_medium_value(self, medium_card, low_card):
        self.board = Board(first_player=self.first_player, modes=[Modes.FALLEN_ACE])
        self.board.play_turn(medium_card, 1, 1)
        self.board.play_turn(low_card, 0, 1)

        assert (
            self.board.get_cell_information_on_position(1, 1)["color"]
            == self.first_player
        )

    @pytest.mark.parametrize(*SANDWICH_INFOS)
    def test_same_with_two_opposing_cards(
        self, card1_pos, card2_pos, high_card, medium_card
    ):
        self.board = Board(first_player=self.first_player, modes=[Modes.SAME])
        self.board.play_turn(high_card, *card1_pos)
        self.board.play_turn(medium_card, 0, 0)
        self.board.play_turn(copy.copy(high_card), *card2_pos)

        self.board.play_turn(copy.copy(high_card), 1, 1)

        assert (
            self.board.get_cell_information_on_position(*card1_pos)["color"]
            == self.second_player
        )
        assert (
            self.board.get_cell_information_on_position(*card2_pos)["color"]
            == self.second_player
        )

    @pytest.mark.parametrize(*SANDWICH_INFOS)
    def test_same_with_one_opposing_card_one_friendly_card(
        self, card1_pos, card2_pos, high_card, medium_card
    ):
        self.board = Board(first_player=self.first_player, modes=[Modes.SAME])
        self.board.play_turn(high_card, *card1_pos)
        self.board.play_turn(copy.copy(high_card), *card2_pos)

        self.board.play_turn(copy.copy(high_card), 1, 1)

        assert (
            self.board.get_cell_information_on_position(*card1_pos)["color"]
            == self.first_player
        )
        assert (
            self.board.get_cell_information_on_position(*card2_pos)["color"]
            == self.first_player
        )

    @pytest.mark.parametrize(*SANDWICH_INFOS)
    def test_plus_with_two_opposing_cards(
        self, card1_pos, card2_pos, high_card, medium_card
    ):
        self.board = Board(first_player=self.first_player, modes=[Modes.PLUS])
        self.board.play_turn(high_card, *card1_pos)
        self.board.play_turn(medium_card, 0, 0)
        self.board.play_turn(copy.copy(high_card), *card2_pos)

        self.board.play_turn(copy.copy(medium_card), 1, 1)

        assert (
            self.board.get_cell_information_on_position(*card1_pos)["color"]
            == self.second_player
        )
        assert (
            self.board.get_cell_information_on_position(*card2_pos)["color"]
            == self.second_player
        )

    def test_same_propagates_to_adjacent_card(self, high_card, medium_card):
        self.board = Board(first_player=self.first_player, modes=[Modes.PLUS])
        self.board.play_turn(high_card, 1, 2)
        self.board.play_turn(copy.copy(medium_card), 0, 0)
        self.board.play_turn(copy.copy(high_card), 1, 0)

        self.board.play_turn(copy.copy(medium_card), 1, 1)

        assert (
            self.board.get_cell_information_on_position(0, 0)["color"]
            == self.second_player
        )
        assert (
            self.board.get_cell_information_on_position(1, 0)["color"]
            == self.second_player
        )
        assert (
            self.board.get_cell_information_on_position(1, 1)["color"]
            == self.second_player
        )
        assert (
            self.board.get_cell_information_on_position(1, 2)["color"]
            == self.second_player
        )

    @pytest.mark.parametrize(*SANDWICH_INFOS)
    def test_plus_with_one_opposing_card_one_friendly_card(
        self, card1_pos, card2_pos, high_card, medium_card
    ):
        self.board = Board(first_player=self.first_player, modes=[Modes.PLUS])
        self.board.play_turn(high_card, *card1_pos)
        self.board.play_turn(copy.copy(high_card), *card2_pos)

        self.board.play_turn(copy.copy(medium_card), 1, 1)

        assert (
            self.board.get_cell_information_on_position(*card1_pos)["color"]
            == self.first_player
        )
        assert (
            self.board.get_cell_information_on_position(*card2_pos)["color"]
            == self.first_player
        )

    def test_plus_propagates_to_adjacent_card(self, high_card, medium_card):
        self.board = Board(first_player=self.first_player, modes=[Modes.PLUS])
        self.board.play_turn(high_card, 1, 2)
        self.board.play_turn(copy.copy(medium_card), 0, 0)
        self.board.play_turn(copy.copy(high_card), 1, 0)

        self.board.play_turn(copy.copy(medium_card), 1, 1)

        assert (
            self.board.get_cell_information_on_position(0, 0)["color"]
            == self.second_player
        )
        assert (
            self.board.get_cell_information_on_position(1, 0)["color"]
            == self.second_player
        )
        assert (
            self.board.get_cell_information_on_position(1, 1)["color"]
            == self.second_player
        )
        assert (
            self.board.get_cell_information_on_position(1, 2)["color"]
            == self.second_player
        )

    def test_ascension_increases_value(self, medium_card):
        self.board = Board(first_player=self.first_player, modes=[Modes.ASCENSION])
        custom_card = copy.copy(medium_card)
        custom_card["type"] = 1
        self.board.play_turn(custom_card, 0, 0)

        card_on_board = self.board.get_cell_information_on_position(0, 0)["card"]
        assert (
            card_on_board["top"]
            == card_on_board["bottom"]
            == card_on_board["left"]
            == card_on_board["right"]
            == medium_card["top"] + 1
        )

    def test_ascension_increases_value_for_other_card_played_too(self, medium_card):
        self.board = Board(first_player=self.first_player, modes=[Modes.ASCENSION])
        custom_card = copy.copy(medium_card)
        custom_card["type"] = 1
        self.board.play_turn(custom_card, 0, 0)

        custom_card2 = copy.copy(medium_card)
        custom_card2["type"] = 1
        self.board.play_turn(custom_card2, 0, 1)

        card_on_board = self.board.get_cell_information_on_position(0, 1)["card"]
        assert (
            card_on_board["top"]
            == card_on_board["bottom"]
            == card_on_board["left"]
            == card_on_board["right"]
            == medium_card["top"] + 2
        )

    def test_ascension_does_not_go_above_10(self, high_card):
        self.board = Board(first_player=self.first_player, modes=[Modes.ASCENSION])
        custom_card = copy.copy(high_card)
        custom_card["type"] = 1
        self.board.play_turn(custom_card, 0, 0)

        card_on_board = self.board.get_cell_information_on_position(0, 0)["card"]
        assert (
            card_on_board["top"]
            == card_on_board["bottom"]
            == card_on_board["left"]
            == card_on_board["right"]
            == high_card["top"]
        )

    def test_descension_decreases_value(self, medium_card):
        self.board = Board(first_player=self.first_player, modes=[Modes.DESCENSION])
        custom_card = copy.copy(medium_card)
        custom_card["type"] = 1
        self.board.play_turn(custom_card, 0, 0)

        card_on_board = self.board.get_cell_information_on_position(0, 0)["card"]
        assert (
            card_on_board["top"]
            == card_on_board["bottom"]
            == card_on_board["left"]
            == card_on_board["right"]
            == medium_card["top"] - 1
        )

    def test_descension_decreases_value_for_other_card_played_too(self, medium_card):
        self.board = Board(first_player=self.first_player, modes=[Modes.DESCENSION])
        custom_card = copy.copy(medium_card)
        custom_card["type"] = 1
        self.board.play_turn(custom_card, 0, 0)

        custom_card2 = copy.copy(medium_card)
        custom_card2["type"] = 1
        self.board.play_turn(custom_card2, 0, 1)

        card_on_board = self.board.get_cell_information_on_position(0, 1)["card"]
        assert (
            card_on_board["top"]
            == card_on_board["bottom"]
            == card_on_board["left"]
            == card_on_board["right"]
            == medium_card["top"] - 2
        )

    def test_descension_does_not_go_below_1(self, low_card):
        self.board = Board(first_player=self.first_player, modes=[Modes.DESCENSION])
        custom_card = copy.copy(low_card)
        custom_card["type"] = 1
        self.board.play_turn(custom_card, 0, 0)

        card_on_board = self.board.get_cell_information_on_position(0, 0)["card"]
        assert (
            card_on_board["top"]
            == card_on_board["bottom"]
            == card_on_board["left"]
            == card_on_board["right"]
            == low_card["top"]
        )

    def test_card_with_type_does_not_change_if_no_modes(self, medium_card):
        self.board = Board(first_player=self.first_player, modes=[])
        custom_card = copy.copy(medium_card)
        custom_card["type"] = 1
        self.board.play_turn(custom_card, 0, 0)

        card_on_board = self.board.get_cell_information_on_position(0, 0)["card"]
        assert (
            card_on_board["top"]
            == card_on_board["bottom"]
            == card_on_board["left"]
            == card_on_board["right"]
            == MEDIUM_VALUE
        )


class TestDisplayBoard(TestBoard):
    def test_display_does_not_crash(self, high_card):
        self.board = Board(first_player=self.first_player, modes=[])
        self.board.play_turn(high_card, 0, 0)
        self.board.play_turn(copy.copy(high_card), 0, 1)
        self.board.display()

    def test_print_does_not_crash(self, high_card):
        self.board = Board(first_player=self.first_player, modes=[])
        self.board.play_turn(high_card, 0, 0)
        self.board.play_turn(copy.copy(high_card), 0, 1)
        self.board.print()


class TestCalculateWinner(TestBoard):
    def test_draw(self, low_card):
        self.board = Board(first_player=self.first_player, modes=[])
        for position in ALL_POSITIONS:
            self.board.play_turn(low_card, *position)

        assert self.board.get_winner() == DRAW

    @pytest.mark.parametrize(
        "first_player, second_player",
        [(Player.BLUE, Player.RED), (Player.RED, Player.BLUE)],
    )
    def test_first_player_wins(self, first_player, second_player, low_card, high_card):
        self.board = Board(first_player=first_player, modes=[])
        index = 0
        for position in ALL_POSITIONS:
            if index % 2:
                self.board.play_turn(low_card, *position)
            else:
                self.board.play_turn(high_card, *position)

            index += 1

        assert self.board.get_winner() == first_player.name

    @pytest.mark.parametrize(
        "first_player, second_player",
        [(Player.BLUE, Player.RED), (Player.RED, Player.BLUE)],
    )
    def test_second_player_wins(self, first_player, second_player, low_card, high_card):
        self.board = Board(first_player=first_player, modes=[])
        index = 0
        for position in ALL_POSITIONS:
            if index % 2:
                self.board.play_turn(high_card, *position)
            else:
                self.board.play_turn(low_card, *position)

            index += 1

        assert self.board.get_winner() == second_player.name
