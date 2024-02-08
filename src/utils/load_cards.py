import json
import os

import requests


ASSETS_CARDS_PATH = "assets/"
CARDS_ALL_FILE_NAME = "cards.json"
CARDS_3_STARS_FILE_NAME = "cards_3.json"
CARDS_4_STARS_FILE_NAME = "cards_4.json"
CARDS_5_STARS_FILE_NAME = "cards_5.json"

ASSETS_IMAGES_PATH = "assets/images/"
ASSETS_IMAGES__BLUE_PATH = f"{ASSETS_IMAGES_PATH}blue/"
ASSETS_IMAGES__RED_PATH = f"{ASSETS_IMAGES_PATH}red/"

RAELYS_API_GET_ALL_CARDS = "https://triad.raelys.com/api/cards"
RAELYS_API_RESULT = "results"

FILE_WRITE_BINARY = "wb"
FILE_WRITE = "w"


def parse_card_info(card):
    return {
        "name": card["name"],
        "id": card["id"],
        "stars": card["stars"],
        "image": card["image"],
        "image_red": card["image_red"],
        "image_blue": card["image_blue"],
        "stats": {
            "top": card["stats"]["numeric"]["top"],
            "left": card["stats"]["numeric"]["left"],
            "right": card["stats"]["numeric"]["right"],
            "bottom": card["stats"]["numeric"]["bottom"],
        },
        "type": card["type"]["id"],
    }


def download_and_save_new_cards():
    response = requests.get(RAELYS_API_GET_ALL_CARDS)
    if response.status_code != 200:
        raise requests.HTTPError(response.content)

    response_content = json.loads(response.content)
    all_cards = []
    cards_3_stars = []
    cards_4_stars = []
    cards_5_stars = []

    for card in response_content[RAELYS_API_RESULT]:
        print(f"Iterating over card {card['id']}")
        maybe_download_and_save_card_images(
            card["id"], card["image"], card["image_blue"], card["image_red"]
        )
        formatted_card = parse_card_info(card)
        all_cards.append(formatted_card)
        match formatted_card["stars"]:
            case 3:
                cards_3_stars.append(formatted_card)
            case 4:
                cards_4_stars.append(formatted_card)
            case 5:
                cards_5_stars.append(formatted_card)
            case _:
                # We don't really care about cards that have less than 3 stars.
                continue

    save_cards(all_cards, cards_3_stars, cards_4_stars, cards_5_stars)


def maybe_download_and_save_card_images(
    card_id, image_url, image_blue_url, image_red_url
):
    card_image_path = f"{ASSETS_IMAGES_PATH}{card_id}.png"
    card_image_blue_path = f"{ASSETS_IMAGES__BLUE_PATH}{card_id}.png"
    card_image_red_path = f"{ASSETS_IMAGES__RED_PATH}{card_id}.png"

    if not os.path.exists(card_image_path):
        download_and_save_card_image(image_url, card_image_path)

    if not os.path.exists(card_image_blue_path):
        download_and_save_card_image(image_blue_url, card_image_blue_path)

    if not os.path.exists(card_image_red_path):
        download_and_save_card_image(image_red_url, card_image_red_path)


def download_and_save_card_image(image_url, destination_file_path):
    response = requests.get(image_url)
    if response.status_code != 200:
        raise requests.HTTPError(response.content)

    with open(destination_file_path, FILE_WRITE_BINARY) as destination_image:
        destination_image.write(response.content)


def save_cards(all_cards, cards_3_stars, cards_4_stars, cards_5_stars):
    write_cards_file(all_cards, f"{ASSETS_CARDS_PATH}{CARDS_ALL_FILE_NAME}")
    write_cards_file(cards_3_stars, f"{ASSETS_CARDS_PATH}{CARDS_3_STARS_FILE_NAME}")
    write_cards_file(cards_4_stars, f"{ASSETS_CARDS_PATH}{CARDS_4_STARS_FILE_NAME}")
    write_cards_file(cards_5_stars, f"{ASSETS_CARDS_PATH}{CARDS_5_STARS_FILE_NAME}")


def write_cards_file(cards_data, destination_file_path):
    with open(destination_file_path, FILE_WRITE) as destination_file:
        json.dump({"cards": cards_data}, destination_file)