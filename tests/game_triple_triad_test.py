import pytest

from game_triple_triad import Board
from game_triple_triad import Modes
from game_triple_triad import Player


def test_board_init():
    board = Board(first_player=Player.BLUE, modes=[])
    assert board.board == [
        [None, None, None],
        [None, None, None],
        [None, None, None],
    ]
    assert board.current_player == Player.BLUE
    assert board.modes == []


@pytest.mark.parametrize("mode, expected", [(mode, [mode]) for mode in Modes])
def test_assert_board_created_with_correct_modes(mode, expected):
    board = Board(first_player=Player.BLUE, modes=[mode])
    assert board.modes == expected
