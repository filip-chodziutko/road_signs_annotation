import sys
import cv2 as cv
import numpy as np

from math import log, pow, ceil
from os import listdir, path, makedirs, rename

# constants
scale_factor = 0.2
MAX_WIDTH = 1200.0
MAX_HEIGHT = 800.0
MIN_SQARE_PX = 128
COLOR = (0, 255, 0)  # green
CLASS_KEYS = ['a', 'b', 'c', 'd', 'x']
USED_IMGS_DIR = '_used'

# global variables
img = None
winname = None
x_start, y_start, x_end, y_end = (0, 0, 0, 0)
drawing, moving = (False, False)


def mouse(event, x, y, flags, params):
    global drawing, moving, x_start, y_start, x_end, y_end
    if event == cv.EVENT_RBUTTONDOWN:
        x_start, y_start = x, y
        drawing = True
        moving = False
        draw_rectangle(x, y)
    if event == cv.EVENT_LBUTTONDOWN:
        moving = True
        drawing = False
        move_rectangle(x, y)

    if event == cv.EVENT_MOUSEMOVE and (drawing or moving):
        if drawing:
            draw_rectangle(x, y)
        elif moving and None not in [x_start, y_start, x_end, y_end]:
            move_rectangle(x, y)

    if event == cv.EVENT_RBUTTONUP:
        drawing = False
    if event == cv.EVENT_LBUTTONUP:
        moving = False


def draw_rectangle(x, y):
    global img, x_start, y_start, x_end, y_end
    x_sign = 1 if x >= x_start else -1
    y_sign = 1 if y >= y_start else -1

    point_dst = max(abs(x_start - x), abs(y_start - y))
    size = max(point_dst, int(MIN_SQARE_PX * scale_factor))

    if 0 <= x_start + x_sign * size <= img.shape[1] and 0 <= y_start + y_sign * size <= img.shape[0]:
        x_end = x_start + x_sign * size
        y_end = y_start + y_sign * size
        shown_img = img.copy()
        cv.rectangle(shown_img, (x_start, y_start), (x_end, y_end), COLOR, thickness=2)
        cv.imshow(winname, shown_img)


def move_rectangle(x, y):
    global img, x_start, y_start, x_end, y_end
    size = max(abs(x_start - x_end), abs(y_start - y_end))
    if x >= 0 and x + size <= img.shape[1]:
        x_start = x
        x_end = x + size
    if y >= 0 and y + size <= img.shape[0]:
        y_start = y
        y_end = y + size
    shown_img = img.copy()
    cv.rectangle(shown_img, (x_start, y_start), (x_end, y_end), COLOR, thickness=2)
    cv.imshow(winname, shown_img)


def save_img(path, original_img):
    global scale_factor, x_start, y_start, x_end, y_end
    scaled_pos = np.array([y_start, y_end, x_start, x_end])
    real_pos = (scaled_pos/scale_factor).astype(int)
    bounded_img_part = original_img[real_pos[0]:real_pos[1], real_pos[2]:real_pos[3]]
    cv.imwrite(path, bounded_img_part)


def get_scale_factor(original_img):
    factor = 1
    height, width, _ = original_img.shape
    if height > 800.0 or width > 1200.0:
        scale = max(height/800.0, width/1200.0)
        pow2_scale = pow(2.0, ceil(log(scale)/log(2)))  # round to nearest higher power of 2
        factor = 1.0/pow2_scale
    return factor


def reset_drawing():
    global drawing, moving, x_start, y_start, x_end, y_end
    x_start, y_start, x_end, y_end = (0, 0, 0, 0)
    drawing, moving = (False, False)


def init():
    if len(sys.argv) != 2:
        sys.exit('Invalid number of parameters!\n'
                 'Exactly one parameter specifying path to directory is required.')
    input_path = sys.argv[1]  # 'C:\\Users\\Filip\\Downloads\\dataset'

    if not path.isdir(input_path):
        sys.exit('Given directory path is not a valid one!')

    files = [file for file in listdir(input_path) if file.endswith(('.jpg', '.jpeg', '.png'))]
    file_count = len(files)
    if file_count <= 0:
        sys.exit('There are no image files in given directory!')

    for class_key in CLASS_KEYS:
        dir_path = path.join(input_path, class_key.upper())
        if not path.exists(dir_path):
            makedirs(dir_path)

    used_path = path.join(input_path, USED_IMGS_DIR)
    if not path.exists(used_path):
        makedirs(used_path)

    return input_path, files, file_count


def main():
    global img, winname, scale_factor
    input_path, files, file_count = init()

    index = 0
    while True:
        file_name = files[index]
        file_path = path.join(input_path, file_name)
        original_img = cv.imread(file_path)

        scale_factor = get_scale_factor(original_img)
        width, height = int(original_img.shape[1] * scale_factor), int(original_img.shape[0] * scale_factor)
        img = cv.resize(original_img, (width, height), interpolation=cv.INTER_AREA)

        winname = file_name
        cv.imshow(winname, img)
        cv.setMouseCallback(winname, mouse)
        key = cv.waitKey(0)

        if cv.getWindowProperty(winname, cv.WND_PROP_VISIBLE) < 1:
            break

        if key == ord('.'):  # '>' used as an arrow
            index = index + 1 if (index + 1) < file_count else file_count-1
            # move file to another directory (mark it as 'used')
            # rename(path.join(input_path, file_name), path.join(input_path, USED_IMGS_DIR, file_name))
            reset_drawing()
            cv.destroyAllWindows()
        # elif key == ord(','):  # '<' used as an arrow
        #     index = index - 1 if (index - 1) >= 0 else file_count - 1
        #     reset_drawing()
        #     cv.destroyAllWindows()
        elif chr(key).lower() in CLASS_KEYS and None not in (x_start, y_start, x_end, y_end):
            tmp_name = '{}_{}_{}_{}'.format(x_start, y_start, abs(x_start-x_end),file_name)
            tmp_path = path.join(input_path, chr(key).upper(), tmp_name)
            save_img(tmp_path, original_img)
        elif key == 27:  # esc
            break


if __name__ == '__main__':
    main()
