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
                   (0.50, 0.10, 0.05),     # smouldering, dark red
                   (0.30, 0.10, 0.10)]     # embers, very dark red

# burnt greys, slightly tinted by terrain
CHAPARRAL_BURNT = EMBERS + 1
FOREST_BURNT = EMBERS + 2
CANYON_BURNT = EMBERS + 3
BURNT_COLOURS = [(0.20, 0.20, 0.15),       # chaparral
                 (0.15, 0.20, 0.15),       # forest
                 (0.52, 0.49, 0.40)]       # canyon
# lake never burns so its entry doesn't matter
BURNT_STATE_OF_TERRAIN = np.array([CHAPARRAL_BURNT, FOREST_BURNT,
                                   CANYON_BURNT, CHAPARRAL_BURNT])

# white, only used for the 'village reached' text
TEXT = CANYON_BURNT + 1

# water drop (water.py): wet for an hour, then damp (a darker version of the
# terrain) until it dries. extinguished = put out by water, never relights
WET = TEXT + 1
# indexed by the unburnt state, e.g. DAMP_STATE_OF_DRAW[DRAW_FOREST] = damp forest
DAMP_STATE_OF_DRAW = np.arange(WET + 1, WET + 1 + terrain_map.NUM_DRAW_STATES)
DAMP_COLOURS = [tuple(0.7 * c for c in colour) for colour in terrain_map.DRAW_COLOURS]
EXTINGUISHED = DAMP_STATE_OF_DRAW[-1] + 1

COLOURS = (terrain_map.DRAW_COLOURS + BURNING_COLOURS + BURNT_COLOURS
           + [(1, 1, 1), (0.55, 0.80, 1.00)] + DAMP_COLOURS + [(0.45, 0.30, 0.15)])
NUM_STATES = len(COLOURS)


def is_unburnt(grid):
    return grid < CATCHING


def is_burning(grid):
    return (grid >= CATCHING) & (grid <= EMBERS)


def has_caught(grid):
    # burning, burnt or put out, not the text, wet or damp states
    return ((grid >= CATCHING) & (grid <= CANYON_BURNT)) | (grid == EXTINGUISHED)
