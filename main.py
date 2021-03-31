import sys
import cv2 as cv
import numpy as np

from math import ceil
from os import listdir, path, makedirs, rename

# constants
MAX_WIDTH = 1600.0
MAX_HEIGHT = 800.0
MIN_SQARE_PX = 128
COLOR = (0, 255, 0)  # green
CLASS_KEYS = ['a', 'b', 'c', 'd', 'x']
USED_IMGS_DIR = '_used'

# global variables
img = None
scale_factor = None
winname = None
x_start, y_start, x_end, y_end = (None, None, None, None)
x_offset, y_offset = (0, 0)
drawing, moving = (False, False)


def mouse(event, x, y, flags, params):
    global drawing, moving, x_start, y_start, x_end, y_end
    if event == cv.EVENT_LBUTTONDOWN:
        x_start, y_start = x, y
        drawing = True
        moving = False
        draw_rectangle(x, y)
    if event == cv.EVENT_RBUTTONDOWN:
        moving = True
        drawing = False
        if None not in [x_start, y_start, x_end, y_end]:
            move_rectangle(x, y)

    if event == cv.EVENT_MOUSEMOVE and (drawing or moving):
        if drawing:
            draw_rectangle(x, y)
        elif moving and None not in [x_start, y_start, x_end, y_end]:
            move_rectangle(x, y)

    if event == cv.EVENT_LBUTTONUP:
        drawing = False
    if event == cv.EVENT_RBUTTONUP:
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


def save_img(dst_path, original_img):
    bounded_img = get_bounded_img(original_img)
    cv.imwrite(dst_path, bounded_img)


def get_bounded_img(original_img):
    global scale_factor, x_start, y_start, x_end, y_end, x_offset, y_offset

    # prepare coordinates for array
    y_arr = np.array([y_start, y_end] if y_start <= y_end else [y_end, y_start])
    x_arr = np.array([x_start, x_end] if x_start <= x_end else [x_end, x_start])

    # calculate cooridantes for original image - resize -> add offset -> cast to int
    y_arr = (y_arr/scale_factor + y_offset).astype(int)
    x_arr = (x_arr/scale_factor + x_offset).astype(int)

    # slice original image
    bounded_img = original_img[y_arr[0]:y_arr[1], x_arr[0]:x_arr[1]]
    return bounded_img


def get_scale_factor(src_img):
    factor = 1
    height, width, _ = src_img.shape
    if height > MAX_HEIGHT or width > MAX_WIDTH:
        scale = ceil(max(height/MAX_HEIGHT, width/MAX_WIDTH))
        factor = 1.0/scale
    return factor


def reset_drawing():
    global drawing, moving, x_start, y_start, x_end, y_end, x_offset, y_offset
    x_start, y_start, x_end, y_end = (None, None, None, None)
    x_offset, y_offset = (0, 0)
    drawing, moving = (False, False)


def zoom(original_img):
    global img, scale_factor, x_start, y_start, x_end, y_end, x_offset, y_offset

    img = get_bounded_img(original_img)
    # offset required - positions on bounded img are relative to the original img
    x_offset = x_start / scale_factor if x_start <= x_end else x_end/scale_factor
    y_offset = y_start / scale_factor if y_start <= y_end else y_end/scale_factor

    scale_factor = get_scale_factor(img)
    w, h = int(img.shape[1]*scale_factor), int(img.shape[0]*scale_factor)
    img = cv.resize(img, (w, h), interpolation=cv.INTER_AREA)


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

    for class_key in CLASS_KEYS:  # make directory for each class
        dir_path = path.join(input_path, class_key.upper())
        if not path.exists(dir_path):
            makedirs(dir_path)

    # make directory for processed images
    used_path = path.join(input_path, USED_IMGS_DIR)
    if not path.exists(used_path):
        makedirs(used_path)

    return input_path, files, file_count


def main():
    global img, winname, scale_factor
    input_path, files, file_count = init()

    index = 0
    load_img = True
    zoomed = False
    while True:
        if load_img:
            load_img = False
            file_name = files[index]
            winname = file_name
            file_path = path.join(input_path, file_name)
            original_img = cv.imread(file_path)
            scale_factor = get_scale_factor(original_img)
            width, height = int(original_img.shape[1] * scale_factor), int(original_img.shape[0] * scale_factor)
            img = cv.resize(original_img, (width, height), interpolation=cv.INTER_AREA)

        cv.imshow(winname, img)
        cv.setMouseCallback(winname, mouse)
        key = cv.waitKey(0)

        if cv.getWindowProperty(winname, cv.WND_PROP_VISIBLE) < 1:  # exit on window close
            break

        if key == ord('.'):  # '>' used as an arrow
            # move file to another directory (mark it as 'used')
            rename(path.join(input_path, file_name), path.join(input_path, USED_IMGS_DIR, file_name))

            if index + 1 < file_count:
                index += 1
            else:
                print("All images processed has been processed.")
                break

            # reset flags and drawing to handle new image
            load_img = True
            zoomed = False
            reset_drawing()
            cv.destroyAllWindows()
        elif chr(key).lower() in CLASS_KEYS and None not in (x_start, y_start, x_end, y_end):
            tmp_name = '{}_{}_{}_{}'.format(x_start, y_start, abs(x_start-x_end), file_name)
            tmp_path = path.join(input_path, chr(key).upper(), tmp_name)
            save_img(tmp_path, original_img)
        elif key == 32 and not zoomed and None not in (x_start, y_start, x_end, y_end):  # space bar
            zoomed = True
            zoom(original_img)
        elif key == 8:  # backspace
            zoomed = False
            reset_drawing()
            load_img = True
        elif key == 27:  # esc
            break


if __name__ == '__main__':
    main()
