"""Burn stages and their heat. Mostly the flaming stage spreads the fire"""

import numpy as np

from . import states
from .settings import MINUTES_PER_STEP


# catching 1 step, flaming 1h, smouldering, embers after half the fuel
CATCH_STEPS = 1
FLAME_STEPS = 60 // MINUTES_PER_STEP
EMBERS_AT = 0.5

# heat multiplies p_burn. our own guesses for now
HEAT_OF_STATE = np.zeros(states.NUM_STATES)
HEAT_OF_STATE[states.CATCHING] = 0.3
HEAT_OF_STATE[states.FLAMING] = 1
HEAT_OF_STATE[states.SMOULDERING] = 0.05
HEAT_OF_STATE[states.EMBERS] = 0.01


def heat_of(state_grid):
    # looks up the heat of every cell at once: the state number is used as the
    # index into HEAT_OF_STATE, so a flaming cell gets 1, chaparral gets 0 etc.
    # capyle gives -100 for neighbours off the edge of the grid, clip turns
    # that into 0 so they count as unburnt (no heat)
    return HEAT_OF_STATE[np.clip(state_grid, 0, None).astype(int)]


def update(grid, burning, fuel, fuel_start):
    # moves burning cells to the next stage based on how long they've burnt
    steps_burnt = fuel_start - fuel
    # fraction of the fuel used, max(.., 1) just avoids dividing by 0 on lakes
    used = steps_burnt / np.maximum(fuel_start, 1)
    flame_over = steps_burnt >= CATCH_STEPS + FLAME_STEPS
    grid[burning & (steps_burnt >= CATCH_STEPS)] = states.FLAMING
    grid[burning & flame_over] = states.SMOULDERING
    grid[burning & flame_over & (used >= EMBERS_AT)] = states.EMBERS
