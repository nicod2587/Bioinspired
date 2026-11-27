"""Writes text onto the grid, one cell per pixel"""

from functools import lru_cache

import matplotlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = ImageFont.truetype(matplotlib.get_data_path() + '/fonts/ttf/DejaVuSans.ttf', 9)


# tiny 3x5 digits for the clock. each string is 5 rows of 3 pixels read
# left to right, top to bottom, 1 = white. e.g. '1' = 010 110 010 010 111
TINY = {'0': '111101101101111', '1': '010110010010111', '2': '111001111100111',
        '3': '111001111001111', '4': '101101111001001', '5': '111100111001111',
        '6': '111100111101111', '7': '111001001001001', '8': '111101111101111',
        '9': '111101111001111', 'h': '100100111101101', ' ': '000000000000000'}


@lru_cache
def tiny_pixels(text):
    glyphs = [np.array([c == '1' for c in TINY[ch]]).reshape(5, 3) for ch in text]
    gap = np.zeros((5, 1), dtype=bool)
    return np.hstack([p for g in glyphs for p in (g, gap)][:-1])


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


def write(grid, lines, text_state, box_state, corner='top', tiny=False):
    # box with 1 cell of padding in the top or bottom right corner
    pixels = tiny_pixels(lines[0]) if tiny else text_pixels(tuple(lines))
    h, w = pixels.shape
    box = np.full((h + 2, w + 2), box_state)
    box[1:-1, 1:-1][pixels] = text_state
    if corner == 'top':
        grid[:h + 2, -(w + 2):] = box
    else:
        grid[-(h + 2):, -(w + 2):] = box
    return grid
