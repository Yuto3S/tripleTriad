import pytest

from src.models.card import Card
from tests.utils.const import HIGH_VALUE
from tests.utils.const import LOW_VALUE
from tests.utils.const import MEDIUM_VALUE


@pytest.fixture
def low_card():
    return Card(
        top=LOW_VALUE,
        left=LOW_VALUE,
        right=LOW_VALUE,
        bottom=LOW_VALUE,
        card_id=0,
        card_type=0,
    )


@pytest.fixture
def medium_card():
    return Card(
        top=MEDIUM_VALUE,
        left=MEDIUM_VALUE,
        right=MEDIUM_VALUE,
        bottom=MEDIUM_VALUE,
        card_id=1,
        card_type=0,
    )


@pytest.fixture
def high_card():
    return Card(
        top=HIGH_VALUE,
        left=HIGH_VALUE,
        right=HIGH_VALUE,
        bottom=HIGH_VALUE,
        card_id=2,
        card_type=0,
    )
