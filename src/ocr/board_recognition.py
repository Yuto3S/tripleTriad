import cv2
import numpy as np


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

    start_x = int(best_match["location"][0] * best_match["ratio"])
    start_y = int(best_match["location"][1] * best_match["ratio"])
    end_x = int((best_match["location"][0] + template_width) * best_match["ratio"])
    end_y = int((best_match["location"][1] + template_height) * best_match["ratio"])

    print(f"(x,y) {start_x, start_y}, (w,h) {end_x, end_y}, best_match {best_match}")

    board = image[start_y:end_y, start_x:end_x]
    # cv2.rectangle(image, (start_x, start_y), (end_x, end_y), (0, 0, 255), 2)

    show_image(board)
