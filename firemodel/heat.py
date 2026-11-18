"""Burn stages. TODO heat - every burning stage is heat 1 for now"""

import numpy as np

from . import states
from .settings import MINUTES_PER_STEP


# catching 1h, flaming 4h, smouldering, embers after half the fuel
CATCH_STEPS = 60 // MINUTES_PER_STEP
FLAME_STEPS = 4 * 60 // MINUTES_PER_STEP
EMBERS_AT = 0.5

HEAT_OF_STATE = np.zeros(states.NUM_STATES)
HEAT_OF_STATE[states.BURNING_STATES] = 1


def heat_of(state_grid):
    # capyle uses -100 off the edge of the grid
    return HEAT_OF_STATE[np.clip(state_grid, 0, None).astype(int)]


def update(grid, burning, fuel, fuel_start):
    steps_burnt = fuel_start - fuel
    used = steps_burnt / np.maximum(fuel_start, 1)
    flame_over = steps_burnt >= CATCH_STEPS + FLAME_STEPS
    grid[burning & (steps_burnt >= CATCH_STEPS)] = states.FLAMING
    grid[burning & flame_over] = states.SMOULDERING
    grid[burning & flame_over & (used >= EMBERS_AT)] = states.EMBERS
