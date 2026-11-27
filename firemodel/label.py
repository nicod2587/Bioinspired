"""Writes text onto the grid, one cell per pixel"""

from functools import lru_cache

import matplotlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = ImageFont.truetype(matplotlib.get_data_path() + '/fonts/ttf/DejaVuSans.ttf', 9)


@lru_cache
def text_pixels(lines):
    # draw without anti-aliasing so every pixel is on or off, then crop
    img = Image.new('1', (200, 12 * len(lines)), 0)
    draw = ImageDraw.Draw(img)
    draw.fontmode = '1'
    for i, line in enumerate(lines):
        draw.text((0, 10 * i), line, font=FONT, fill=1)
    pixels = np.array(img)
    rows, cols = np.where(pixels)
    return pixels[rows.min():rows.max() + 1, cols.min():cols.max() + 1]


def write(grid, lines, text_state, box_state):
    # box with 1 cell of padding in the top right corner
    pixels = text_pixels(tuple(lines))
    h, w = pixels.shape
    box = np.full((h + 2, w + 2), box_state)
    box[1:-1, 1:-1][pixels] = text_state
    grid[:h + 2, -(w + 2):] = box
    return grid
