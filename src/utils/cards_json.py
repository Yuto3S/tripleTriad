import json


def load_cards():
    with open("assets/cards.json") as cards_json:
        cards_x = json.load(cards_json)

    return cards_x


def load_cards_stars(stars):
    with open(f"assets/cards_{stars}.json") as cards_json:
        cards = json.load(cards_json)

    return cards


def save_x_stars(stars, cards):
    tmp_cards = []
    for card in cards["cards"]:
        if card["stars"] == stars:
            tmp_cards.append(card)

    save_cards(stars, tmp_cards)


def save_cards(stars, cards):
    with open(f"cards_{stars}.json", "w") as cards_json:
        json.dump({"cards": cards}, cards_json)
