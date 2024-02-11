import cv2
import numpy as np


NORMALIZED_BOARD_WIDTH = 1152
NORMALIZED_BOARD_HEIGHT = 488


def show_image(image):
    cv2.imshow("", image)
    cv2.waitKey(0)


# https://pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/
def get_board_from_on_image(board_number):
    image = cv2.imread(f"assets/test_images/board_{board_number}.png")
    template = cv2.imread("assets/images/board_cut.jpg")
    image_height, image_width, _ = image.shape
    template_height, template_width, _ = template.shape

    best_match = None

    # TODO(): Improve area narrowing down with a better algorithm, maybe binary search?
    for scale in np.linspace(0.5, 1.5, 100)[::-1]:
        resized_width = int(image_width * scale)
        resized_height = int(image_height * scale)
        ratio = image_width / float(resized_width)

        if resized_width < template_width or resized_height < template_height:
            break

        resized = cv2.resize(
            image, (resized_width, resized_height), interpolation=cv2.INTER_AREA
        )
        result_match_template = cv2.matchTemplate(
            resized, template, cv2.TM_CCOEFF_NORMED
        )
        _, max_value, _, max_location = cv2.minMaxLoc(result_match_template)

        if best_match is None or max_value > best_match["value"]:
            best_match = {
                "value": max_value,
                "location": max_location,
                "ratio": ratio,
            }

    board_trim_coordinates = get_board_coordinates(
        best_match, template_width, template_height
    )

    board = image[
        board_trim_coordinates["start"]["y"] : board_trim_coordinates["end"]["y"],
        board_trim_coordinates["start"]["x"] : board_trim_coordinates["end"]["x"],
    ]
    normalized_board = cv2.resize(
        board,
        (NORMALIZED_BOARD_WIDTH, NORMALIZED_BOARD_HEIGHT),
        interpolation=cv2.INTER_AREA,
    )
    return normalized_board


def get_board_coordinates(best_match, template_width, template_height):
    start_x = int(best_match["location"][0] * best_match["ratio"])
    start_y = int(best_match["location"][1] * best_match["ratio"])
    end_x = int((best_match["location"][0] + template_width) * best_match["ratio"])
    end_y = int((best_match["location"][1] + template_height) * best_match["ratio"])

    return {
        "start": {
            "x": start_x,
            "y": start_y,
        },
        "end": {
            "x": end_x,
            "y": end_y,
        },
    }


def get_cards_from_board(board):
    # normalized = cv2.resize(
    #     board, (628, 266), interpolation=cv2.INTER_AREA
    # )
    # TOP_LEFT_X = (6, 70) # 64 --> 104 1.625
    # TOP_LEFT_Y = (96, 171)

    TOP_LEFT_X = (13, 128)
    TOP_LEFT_Y = (176, 314)

    # TOP_LEFT_X_START_RATIO = int(TOP_LEFT_X[0] * 100 / WIDTH * 100)
    # TOP_LEFT_X_END_RATIO = int(TOP_LEFT_X[1] / WIDTH * 100)
    # TOP_LEFT_Y_START_RATIO = int(TOP_LEFT_Y[0] / HEIGHT * 100)
    # TOP_LEFT_Y_END_RATIO = int(TOP_LEFT_Y[1] / HEIGHT * 100)

    # print(f"({TOP_LEFT_X_START_RATIO},{TOP_LEFT_Y_START_RATIO}) -> ({TOP_LEFT_X_END_RATIO}, {TOP_LEFT_Y_END_RATIO})")
    # board_height, board_width, _ = board.shape
    #

    print(f"({TOP_LEFT_X[0]}, {TOP_LEFT_Y[0]}) -> ({TOP_LEFT_X[1]}, {TOP_LEFT_Y[1]})")

    cv2.rectangle(
        board,
        (TOP_LEFT_X[0], TOP_LEFT_Y[0]),
        (TOP_LEFT_X[1], TOP_LEFT_Y[1]),
        (0, 0, 255),
        2,
    )

    show_image(board)
