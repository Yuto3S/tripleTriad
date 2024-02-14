import json
import os

import requests


GENERATED_ASSETS_PATH = "assets/generated/"


CARDS_ALL_FILE_NAME = "cards.json"
CARDS_3_STARS_FILE_NAME = "cards_3.json"
CARDS_4_STARS_FILE_NAME = "cards_4.json"
CARDS_5_STARS_FILE_NAME = "cards_5.json"
NUMBER_OF_STARS_TO_FILE_PATH = {
    "3": f"{GENERATED_ASSETS_PATH}{CARDS_3_STARS_FILE_NAME}",
    "4": f"{GENERATED_ASSETS_PATH}{CARDS_4_STARS_FILE_NAME}",
    "5": f"{GENERATED_ASSETS_PATH}{CARDS_5_STARS_FILE_NAME}",
}

IMAGES_PATH = "assets/images/"
CARDS_IMAGES_PATH = f"{IMAGES_PATH}card/"
CARDS_IMAGES__DEFAULT_PATH = f"{CARDS_IMAGES_PATH}default/"
CARDS_IMAGES__BLUE_PATH = f"{CARDS_IMAGES_PATH}blue/"
CARDS_IMAGES__RED_PATH = f"{CARDS_IMAGES_PATH}red/"

BOARD_IMAGES_PATH = f"{IMAGES_PATH}/board/"
BOARD_TEMPLATE_IMAGE_PATH = f"{BOARD_IMAGES_PATH}board_cut.jpg"

RAELYS_API_GET_ALL_CARDS = "https://triad.raelys.com/api/cards"
RAELYS_API_RESULT = "results"
RAELYS_API_ID = "id"
RAELYS_API_IMAGE = "image"
RAELYS_API_BLUE_IMAGE = "image_blue"
RAELYS_API_RED_IMAGE = "image_red"


FILE_WRITE_BINARY = "wb"
FILE_WRITE = "w"

FILE_FORMAT_PNG = ".png"


# TODO() See how to create dict class
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
            card[RAELYS_API_ID],
            card[RAELYS_API_IMAGE],
            card[RAELYS_API_BLUE_IMAGE],
            card[RAELYS_API_RED_IMAGE],
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
                # No specific treatment for cards with less than 3 stars.
                continue

    save_cards(all_cards, cards_3_stars, cards_4_stars, cards_5_stars)


def maybe_download_and_save_card_images(
    card_id, image_url, image_blue_url, image_red_url
):
    card_image_path = f"{CARDS_IMAGES__DEFAULT_PATH}{card_id}{FILE_FORMAT_PNG}"
    card_image_blue_path = f"{CARDS_IMAGES__BLUE_PATH}{card_id}{FILE_FORMAT_PNG}"
    card_image_red_path = f"{CARDS_IMAGES__RED_PATH}{card_id}{FILE_FORMAT_PNG}"

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
    write_cards_file(all_cards, f"{GENERATED_ASSETS_PATH}{CARDS_ALL_FILE_NAME}")
    write_cards_file(cards_3_stars, NUMBER_OF_STARS_TO_FILE_PATH.get("3"))
    write_cards_file(cards_4_stars, NUMBER_OF_STARS_TO_FILE_PATH.get("4"))
    write_cards_file(cards_5_stars, NUMBER_OF_STARS_TO_FILE_PATH.get("5"))


def write_cards_file(cards_data, destination_file_path):
    with open(destination_file_path, FILE_WRITE) as destination_file:
        json.dump({"cards": cards_data}, destination_file)
