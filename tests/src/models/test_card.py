import pytest

from src.models.card import Card
from src.models.card import MAX_ASCEND
from src.models.card import MIN_DESCEND

DEFAULT_TOP = 2
DEFAULT_BOTTOM = 3
DEFAULT_LEFT = 4
DEFAULT_RIGHT = 5


class TestCard:
    def _init_custom_card(self):
        self.card = Card(
            top=DEFAULT_TOP,
            bottom=DEFAULT_BOTTOM,
            left=DEFAULT_LEFT,
            right=DEFAULT_RIGHT,
            card_id=100,
            card_type=0,
        )

    def _init_custom_card_with_game_id(self, game_id):
        self.card = Card(
            top=DEFAULT_TOP,
            bottom=DEFAULT_BOTTOM,
            left=DEFAULT_LEFT,
            right=DEFAULT_RIGHT,
            card_id=100,
            card_type=0,
            game_id=game_id,
        )

    def test_card_init(self):
        self._init_custom_card()
        assert self.card.top == DEFAULT_TOP
        assert self.card.bottom == DEFAULT_BOTTOM
        assert self.card.left == DEFAULT_LEFT
        assert self.card.right == DEFAULT_RIGHT
        assert self.card.card_id == 100
        assert self.card.card_type == 0
        assert self.card.game_id is None

    def test_card_game_id(self):
        some_custom_game_id = "SOME_CUSTOM_GAME_ID"
        self._init_custom_card_with_game_id(some_custom_game_id)
        assert self.card.game_id == some_custom_game_id

    def test_card_updates_game_id_if_game_is_is_none(self):
        updated_game_id = "UPDATED_GAME_ID"
        self._init_custom_card()
        self.card.update_game_id(updated_game_id)
        assert self.card.game_id == f"{self.card.card_id}{updated_game_id}"

    def test_card_updates_game_id_does_nothing_if_already_defined(self):
        some_custom_game_id = "SOME_CUSTOM_GAME_ID"
        updated_game_id = "UPDATED_GAME_ID"
        self._init_custom_card_with_game_id(some_custom_game_id)
        self.card.update_game_id(updated_game_id)
        assert self.card.game_id == some_custom_game_id

    def test_ascend_increases_by_one(self):
        self._init_custom_card()
        self.card.ascend()
        assert self.card.top == DEFAULT_TOP + 1
        assert self.card.bottom == DEFAULT_BOTTOM + 1
        assert self.card.left == DEFAULT_LEFT + 1
        assert self.card.right == DEFAULT_RIGHT + 1

    def test_ascend_does_not_go_above_10(self):
        self._init_custom_card()
        for _ in range(0, 20):
            self.card.ascend()

        assert self.card.top == MAX_ASCEND
        assert self.card.bottom == MAX_ASCEND
        assert self.card.left == MAX_ASCEND
        assert self.card.right == MAX_ASCEND

    def test_descend_increases_by_one(self):
        self._init_custom_card()
        self.card.descend()
        assert self.card.top == DEFAULT_TOP - 1
        assert self.card.bottom == DEFAULT_BOTTOM - 1
        assert self.card.left == DEFAULT_LEFT - 1
        assert self.card.right == DEFAULT_RIGHT - 1

    def test_descend_does_not_go_below_1(self):
        self._init_custom_card()
        for _ in range(0, 20):
            self.card.descend()

        assert self.card.top == MIN_DESCEND
        assert self.card.bottom == MIN_DESCEND
        assert self.card.left == MIN_DESCEND
        assert self.card.right == MIN_DESCEND

    @pytest.mark.parametrize(
        "direction, expected_value",
        [
            ("top", DEFAULT_TOP),
            ("bottom", DEFAULT_BOTTOM),
            ("left", DEFAULT_LEFT),
            ("right", DEFAULT_RIGHT),
        ],
    )
    def test_get_direction_value(self, direction, expected_value):
        self._init_custom_card()
        assert self.card.get_direction(direction) == expected_value

    def test_get_direction_value_raises_error_if_wrong_direction(self):
        self._init_custom_card()
        with pytest.raises(Exception):
            self.card.get_direction("random_direction")

    @pytest.mark.parametrize(
        "direction, expected_value",
        [
            ("top", DEFAULT_BOTTOM),
            ("bottom", DEFAULT_TOP),
            ("left", DEFAULT_RIGHT),
            ("right", DEFAULT_LEFT),
        ],
    )
    def test_get_opposite_direction_value(self, direction, expected_value):
        self._init_custom_card()
        assert self.card.get_opposite_direction(direction) == expected_value

    def test_get_opposite_direction_value_raises_error_if_wrong_direction(self):
        self._init_custom_card()
        with pytest.raises(Exception):
            self.card.get_opposite_direction("random_direction")
