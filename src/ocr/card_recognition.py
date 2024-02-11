import os.path

import cv2
import numpy as np
from keras.applications.vgg16 import preprocess_input
from keras.applications.vgg16 import VGG16
from keras.models import Model
from keras.preprocessing import image
from PIL import Image

# https://stackoverflow.com/a/71967670


def extract(img, model):
    img = img.resize((224, 224))  # Resize the image
    img = img.convert("RGB")  # Convert the image color space
    x = image.img_to_array(img)  # Reformat the image
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    # TODO send all x at once
    # https://www.tensorflow.org/api_docs/python/tf/keras/Model#predict
    feature = model.predict(x)[0]  # Extract Features
    return feature / np.linalg.norm(feature)


def test_one_to_many(input_img_name):
    base_model = VGG16(weights="imagenet")
    model = Model(inputs=base_model.input, outputs=base_model.get_layer("fc1").output)

    # Iterate through images and extract Features
    images = [f"assets/images/{i}.png" for i in range(1, 404)]

    if os.path.exists("tmp_features.npy"):
        all_features = np.load("tmp_features.npy")
    else:
        all_features = np.zeros(shape=(len(images), 4096))

        for i in range(len(images)):
            feature = extract(img=Image.open(images[i]), model=model)
            all_features[i] = np.array(feature)

        np.save("tmp_features", np.array(all_features))

    # Match image
    query = extract(
        img=Image.open(f"assets/test_images/{input_img_name}.png"), model=model
    )  # Extract its features
    dists = np.linalg.norm(
        all_features - query, axis=1
    )  # Calculate the similarity (distance) between images
    ids = np.argsort(dists)[:5]  # Extract 5 images that have lowest distance
    # print(ids)
    print(f"Card should be: {ids[0]+1}")
    return ids[0] + 1


# https://medium.com/@developerRegmi/image-similarity-comparison-using-vgg16-deep-learning-model-a663a411cd24
def test_one_to_from_image(img_open_cv):
    base_model = VGG16(weights="imagenet")
    model = Model(inputs=base_model.input, outputs=base_model.get_layer("fc1").output)

    # Iterate through images and extract Features
    images = [f"assets/images/{i}.png" for i in range(1, 404)]

    if os.path.exists("tmp_features.npy"):
        all_features = np.load("tmp_features.npy")
    else:
        all_features = np.zeros(shape=(len(images), 4096))

        for i in range(len(images)):
            feature = extract(img=Image.open(images[i]), model=model)
            all_features[i] = np.array(feature)

        np.save("tmp_features", np.array(all_features))

    # Match image
    img_open_cv = cv2.cvtColor(img_open_cv, cv2.COLOR_BGR2RGB)
    query = extract(
        img=Image.fromarray(img_open_cv), model=model
    )  # Extract its features
    dists = np.linalg.norm(
        all_features - query, axis=1
    )  # Calculate the similarity (distance) between images
    # TODO(): Maybe define a minimum distance
    ids = np.argsort(dists)[:5]  # Extract 5 images that have lowest distance
    # print(ids)
    print(f"Card should be: {ids[0]+1}")
    return ids[0] + 1
