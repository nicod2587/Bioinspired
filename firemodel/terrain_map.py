"""The map from figure 1 of the brief.

make_map() gives the terrain of each cell, draw_states() turns it into
the starting states so each terrain has its own colour.
Run this file to save a picture of the map in screenshots/.
"""

import numpy as np


# terrain types (same order as the tables in burn.py)
CHAPARRAL = 0
FOREST = 1
CANYON = 2
LAKE = 3

# 200m cells so the 50km map is 250x250. 50m and 100m were too slow in capyle.
# everything below is in km so changing CELL_KM still gives the same map
MAP_KM = 50
CELL_KM = 0.2
GRID_SIZE = int(round(MAP_KM / CELL_KM))
GRID_DIMS = (GRID_SIZE, GRID_SIZE)

# fixed seed so the map is the same every run
MAP_SEED = 3524

# (x0, x1, y0, y1) in km, x is east and y is north, read off figure 1
FOREST_AREAS = [(0, 25, 43, 45),
                (5, 12.5, 20, 43),
                (5, 25, 15, 20),
                (32.5, 45, 35, 40)]
LAKE_AREAS = [(17.5, 22.5, 27.5, 37.5),
              (37.5, 39.5, 10, 22.5)]
CANYON_AREA = (25, 45, 25.5, 27.5)
# town is 2.5 x 2.5 km centred on (20, 5)
TOWN_AREA = (18.75, 21.25, 3.75, 6.25)

# how ragged the forest edge is and how round the canyon/lake corners are
FOREST_EDGE_KM = 0.4
CANYON_CORNER_KM = 0.5
LAKE_CORNER_KM = 0.5


def km_to_cells(km):
    # round() rounds halves to even, this always rounds them up
    return int(np.floor(km / CELL_KM + 0.5))


def km_rect(x0, x1, y0, y1):
    """rows and cols for a rectangle in km. row 0 is the top (north)"""
    rows = slice(km_to_cells(MAP_KM - y1), km_to_cells(MAP_KM - y0))
    cols = slice(km_to_cells(x0), km_to_cells(x1))
    return rows, cols


TOWN_ROWS, TOWN_COLS = km_rect(*TOWN_AREA)
# fire start points (row, col)
POWER_PLANT = (0, 0)
INCINERATOR = (0, GRID_SIZE - 1)


def smooth(a, radius, passes=1):
    """box blur, each cell becomes the average of the cells around it"""
    size = 2 * radius + 1
    rows, cols = a.shape
    for _ in range(passes):
        padded = np.pad(a, ((0, 0), (radius, radius)), mode='reflect')
        a = sum(padded[:, i:i + cols] for i in range(size)) / size
        padded = np.pad(a, ((radius, radius), (0, 0)), mode='reflect')
        a = sum(padded[i:i + rows, :] for i in range(size)) / size
    return a


def smooth_noise(rng, radius, passes):
    """blurred random noise between -1 and 1"""
    noise = smooth(rng.random_sample(GRID_DIMS), radius, passes)
    noise -= noise.mean()
    return noise / np.abs(noise).max()


def rounded_rect(x0, x1, y0, y1, corner_km):
    """True inside a rectangle (km) with rounded corners"""
    rows, cols = np.indices(GRID_DIMS)
    x = (cols + 0.5) * CELL_KM
    y = MAP_KM - (rows + 0.5) * CELL_KM
    # distance to the rectangle shrunk by corner_km
    dx = np.maximum(0, np.maximum((x0 + corner_km) - x, x - (x1 - corner_km)))
    dy = np.maximum(0, np.maximum((y0 + corner_km) - y, y - (y1 - corner_km)))
    return dx ** 2 + dy ** 2 <= corner_km ** 2


def ragged_forest(rng):
    """True for forest. the brief's rectangles but with rough edges"""
    forest = np.zeros(GRID_DIMS)
    for area in FOREST_AREAS:
        forest[km_rect(*area)] = 1
    # blur the edges and wobble them a bit so they aren't straight
    amount = smooth(forest, km_to_cells(FOREST_EDGE_KM), passes=2)
    wobble = smooth_noise(rng, km_to_cells(1.0), passes=3)
    amount = np.clip(amount + 2 * amount * (1 - amount) * wobble, 0, 1)
    # forest if the amount is over a random threshold, so the edge is patchy.
    # threshold is around 0.4 so the forest grows out a bit, clipped so
    # there are no lone trees far out or holes in the middle
    threshold = np.clip(0.4 + 0.3 * smooth_noise(rng, 1, passes=1), 0.1, 0.9)
    return amount >= threshold


def make_map():
    """terrain of every cell"""
    rng = np.random.RandomState(MAP_SEED)
    terrain = np.full(GRID_DIMS, CHAPARRAL)
    terrain[ragged_forest(rng)] = FOREST
    terrain[rounded_rect(*CANYON_AREA, corner_km=CANYON_CORNER_KM)] = CANYON
    for area in LAKE_AREAS:
        terrain[rounded_rect(*area, corner_km=LAKE_CORNER_KM)] = LAKE
    return terrain


def town_mask():
    """True for town cells"""
    mask = np.zeros(GRID_DIMS, dtype=bool)
    mask[TOWN_ROWS, TOWN_COLS] = True
    return mask


# capyle has one colour per state, so each terrain gets its own unburnt state.
# these are only for colour, burning is worked out in burn.py
DRAW_CHAPARRAL = 0
DRAW_FOREST = 1
DRAW_CANYON = 2
DRAW_LAKE = 3
DRAW_TOWN = 4
DRAW_COLOURS = [(0.76, 0.75, 0.15),    # chaparral
                (0.25, 0.40, 0.15),    # dense forest
                (1.00, 1.00, 0.30),    # canyon
                (0.16, 0.36, 0.58),    # lake
                (0.00, 0.00, 0.00)]    # town
NUM_DRAW_STATES = len(DRAW_COLOURS)


def draw_states(terrain):
    """starting state of every cell"""
    draw = np.full(GRID_DIMS, DRAW_CHAPARRAL)
    draw[terrain == FOREST] = DRAW_FOREST
    draw[terrain == CANYON] = DRAW_CANYON
    draw[terrain == LAKE] = DRAW_LAKE
    draw[town_mask()] = DRAW_TOWN
    return draw


if __name__ == "__main__":
    import os
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    image = np.array(DRAW_COLOURS)[draw_states(make_map())]
    fig, ax = plt.subplots(figsize=(9, 9))
    ax.imshow(image, extent=(0, MAP_KM, 0, MAP_KM), interpolation='none')
    ax.set_xlabel('km east')
    ax.set_ylabel('km north')
    ax.set_title('Terrain map, {:g} m cells ({} x {})'.format(
        CELL_KM * 1000, *GRID_DIMS))
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(project_dir, 'screenshots', 'terrain_map.png')
    fig.savefig(out, dpi=150, bbox_inches='tight')
    print('saved', out)
