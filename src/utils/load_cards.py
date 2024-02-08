import json
import os

import requests


ASSETS_IMAGES_PATH = "assets/images/"
ASSETS_IMAGES__BLUE_PATH = f"{ASSETS_IMAGES_PATH}blue/"
ASSETS_IMAGES__RED_PATH = f"{ASSETS_IMAGES_PATH}red/"

RAELYS_API_GET_ALL_CARDS = "https://triad.raelys.com/api/cards"
RAELYS_API_RESULT = "results"

WRITE_BINARY = "wb"


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

    for card in response_content[RAELYS_API_RESULT]:
        # print(card)
        print(parse_card_info(card))
        maybe_get_card_images(
            card["id"], card["image"], card["image_blue"], card["image_red"]
        )
        break


def maybe_get_card_images(card_id, image_url, image_blue_url, image_red_url):
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

    with open(destination_file_path, WRITE_BINARY) as destination_image:
        destination_image.write(response.content)
