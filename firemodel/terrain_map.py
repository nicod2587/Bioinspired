"""Map from figure 1 of the brief. Run this file to save a picture of it."""

import numpy as np


# terrain types, same order as the tables in burn.py
CHAPARRAL = 0
FOREST = 1
CANYON = 2
LAKE = 3

# 200m cells -> 250x250. tried 50m and 100m but capyle was too slow
MAP_KM = 50
CELL_KM = 0.2
GRID_SIZE = int(round(MAP_KM / CELL_KM))
GRID_DIMS = (GRID_SIZE, GRID_SIZE)

MAP_SEED = 3524

# (x0, x1, y0, y1) in km, x = east, y = north
FOREST_AREAS = [(0, 25, 43, 45),
                (5, 12.5, 20, 43),
                (5, 25, 15, 20),
                (32.5, 45, 35, 40)]
LAKE_AREAS = [(17.5, 22.5, 27.5, 37.5),
              (37.5, 39.5, 10, 22.5)]
CANYON_AREA = (25, 45, 25.5, 27.5)
TOWN_AREA = (18.75, 21.25, 3.75, 6.25)   # 2.5km square around (20, 5)

FOREST_EDGE_KM = 0.4
CANYON_CORNER_KM = 0.5
LAKE_CORNER_KM = 0.5


def km_to_cells(km):
    # not round() because that rounds 0.5 to even
    return int(np.floor(km / CELL_KM + 0.5))


def km_rect(x0, x1, y0, y1):
    # row 0 is the top of the map so y is flipped
    rows = slice(km_to_cells(MAP_KM - y1), km_to_cells(MAP_KM - y0))
    cols = slice(km_to_cells(x0), km_to_cells(x1))
    return rows, cols


TOWN_ROWS, TOWN_COLS = km_rect(*TOWN_AREA)
POWER_PLANT = (0, 0)
INCINERATOR = (0, GRID_SIZE - 1)


def smooth(a, radius, passes=1):
    # box blur
    size = 2 * radius + 1
    rows, cols = a.shape
    for _ in range(passes):
        padded = np.pad(a, ((0, 0), (radius, radius)), mode='reflect')
        a = sum(padded[:, i:i + cols] for i in range(size)) / size
        padded = np.pad(a, ((radius, radius), (0, 0)), mode='reflect')
        a = sum(padded[i:i + rows, :] for i in range(size)) / size
    return a


def smooth_noise(rng, radius, passes):
    # blurred noise scaled to -1..1
    noise = smooth(rng.random_sample(GRID_DIMS), radius, passes)
    noise -= noise.mean()
    return noise / np.abs(noise).max()


def rounded_rect(x0, x1, y0, y1, corner_km):
    rows, cols = np.indices(GRID_DIMS)
    x = (cols + 0.5) * CELL_KM
    y = MAP_KM - (rows + 0.5) * CELL_KM
    dx = np.maximum(0, np.maximum((x0 + corner_km) - x, x - (x1 - corner_km)))
    dy = np.maximum(0, np.maximum((y0 + corner_km) - y, y - (y1 - corner_km)))
    return dx ** 2 + dy ** 2 <= corner_km ** 2


def ragged_forest(rng):
    forest = np.zeros(GRID_DIMS)
    for area in FOREST_AREAS:
        forest[km_rect(*area)] = 1
    # blur + noise so the edges aren't straight lines
    amount = smooth(forest, km_to_cells(FOREST_EDGE_KM), passes=2)
    wobble = smooth_noise(rng, km_to_cells(1.0), passes=3)
    amount = np.clip(amount + 2 * amount * (1 - amount) * wobble, 0, 1)
    # random threshold makes the edge patchy. clipped so no stray trees/holes
    threshold = np.clip(0.4 + 0.3 * smooth_noise(rng, 1, passes=1), 0.1, 0.9)
    return amount >= threshold


def make_map():
    rng = np.random.RandomState(MAP_SEED)
    terrain = np.full(GRID_DIMS, CHAPARRAL)
    terrain[ragged_forest(rng)] = FOREST
    terrain[rounded_rect(*CANYON_AREA, corner_km=CANYON_CORNER_KM)] = CANYON
    for area in LAKE_AREAS:
        terrain[rounded_rect(*area, corner_km=LAKE_CORNER_KM)] = LAKE
    return terrain


def town_mask():
    mask = np.zeros(GRID_DIMS, dtype=bool)
    mask[TOWN_ROWS, TOWN_COLS] = True
    return mask


# unburnt states, one per terrain so they get different colours in capyle
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
