import json

from src.ocr.card_recognition import GENERATED_ASSETS_PATH
from src.utils.download_cards import CARDS_ALL_FILE_NAME


def load_cards():
    with open(f"{GENERATED_ASSETS_PATH}{CARDS_ALL_FILE_NAME}") as cards_json:
        cards_x = json.load(cards_json)

    return cards_x


def load_cards_stars(stars):
    with open(f"{GENERATED_ASSETS_PATH}cards_{stars}.json") as cards_json:
        cards = json.load(cards_json)

    return cards


def save_x_stars(stars, cards):
    tmp_cards = []
    for card in cards["cards"]:
        if card["stars"] == stars:
            tmp_cards.append(card)

    save_cards(stars, tmp_cards)


def save_cards(stars, cards):
    with open(f"{GENERATED_ASSETS_PATH}cards_{stars}.json", "w") as cards_json:
        json.dump({"cards": cards}, cards_json)
