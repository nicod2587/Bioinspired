"""States and colours: unburnt (from terrain_map), then burning, then burnt."""

import numpy as np

from . import terrain_map


# timings in heat.py
CATCHING = terrain_map.NUM_DRAW_STATES
FLAMING = CATCHING + 1
SMOULDERING = CATCHING + 2
EMBERS = CATCHING + 3
BURNING_STATES = [CATCHING, FLAMING, SMOULDERING, EMBERS]
BURNING_COLOURS = [(0.85, 0.20, 0.05),     # catching, red
                   (1.00, 0.85, 0.25),     # flaming, yellow
                   (0.95, 0.45, 0.05),     # smouldering, orange
                   (0.50, 0.08, 0.03)]     # embers, dark red

# burnt greys, slightly tinted by terrain
CHAPARRAL_BURNT = EMBERS + 1
FOREST_BURNT = EMBERS + 2
CANYON_BURNT = EMBERS + 3
BURNT_COLOURS = [(0.30, 0.29, 0.24),       # chaparral
                 (0.26, 0.29, 0.24),       # forest
                 (0.52, 0.49, 0.40)]       # canyon
# lake never burns so its entry doesn't matter
BURNT_STATE_OF_TERRAIN = np.array([CHAPARRAL_BURNT, FOREST_BURNT,
                                   CANYON_BURNT, CHAPARRAL_BURNT])

COLOURS = terrain_map.DRAW_COLOURS + BURNING_COLOURS + BURNT_COLOURS
NUM_STATES = len(COLOURS)


def is_unburnt(grid):
    return grid < CATCHING


def is_burning(grid):
    return (grid >= CATCHING) & (grid <= EMBERS)
