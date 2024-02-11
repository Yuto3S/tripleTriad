import glob

import cv2
import numpy as np
from keras.applications.vgg16 import preprocess_input
from keras.applications.vgg16 import VGG16
from keras.models import Model
from keras.preprocessing import image
from PIL import Image

from src.utils.download_cards import ASSETS_IMAGES__DEFAULT_PATH

VGG16_INPUT_SIZE = 224
RGB = "RGB"


def generate_embeddings_for_all_existing_cards():
    model = get_deep_learning_model()

    # TODO() move files into a sub directory separate from the blue/red folders
    number_of_cards = len(
        [file for file in glob.glob(f"{ASSETS_IMAGES__DEFAULT_PATH}*.png")]
    )

    all_embeddings = []
    for card_image in get_images(number_of_cards):
        embeddings = extract_embeddings_from_image(card_image, model)
        all_embeddings.append(embeddings)

    np.save("tmp_test_test", np.array(all_embeddings))


def get_deep_learning_model():
    base_model = VGG16()
    return Model(inputs=base_model.input, outputs=base_model.get_layer("fc1").output)


def get_images(number_of_cards):
    for card_number in range(1, number_of_cards + 1):
        card_image = Image.open(f"assets/images/{card_number}.png")
        yield card_image


# Inspired from https://stackoverflow.com/a/71967670
def extract_embeddings_from_image(img, model):
    img_as_array = transform_and_prepare_image_for_vgg16(img)
    embeddings = model.predict(img_as_array)[0]
    normalized_embeddings = normalize_embeddings(embeddings)

    return normalized_embeddings


def transform_and_prepare_image_for_vgg16(img):
    img = img.resize((VGG16_INPUT_SIZE, VGG16_INPUT_SIZE))
    img = img.convert(RGB)

    img_as_array = image.img_to_array(img)
    img_as_array = np.expand_dims(img_as_array, axis=0)
    img_as_array = preprocess_input(img_as_array)

    return img_as_array


def normalize_embeddings(embeddings):
    return embeddings / np.linalg.norm(embeddings)


# https://medium.com/@developerRegmi/image-similarity-comparison-using-vgg16-deep-learning-model-a663a411cd24
def find_ids_of_cards(cards_image):
    model = get_deep_learning_model()
    all_embeddings = np.load("tmp_test_test.npy")

    matched_cards_id = []

    for card_image in cards_image:
        card_image = cv2.cvtColor(card_image, cv2.COLOR_BGR2RGB)
        card_img = Image.fromarray(card_image)
        embeddings = extract_embeddings_from_image(card_img, model)
        card_best_match_id = find_best_match(embeddings, all_embeddings)

        matched_cards_id.append(card_best_match_id)

    return matched_cards_id


def find_best_match(embeddings, all_embeddings):
    distances_between_embeddings = np.linalg.norm(all_embeddings - embeddings, axis=1)
    return np.argsort(distances_between_embeddings)[0] + 1
