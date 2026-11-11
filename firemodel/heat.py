"""Burn stages and heat.

For now this just moves burning cells through the stages so they change
colour. Heat doesn't do anything yet, every burning stage has heat 1.
"""

import numpy as np

from . import states
from .settings import MINUTES_PER_STEP


# catching for 1 hour, flaming for 4 hours, then smouldering,
# then embers once half the fuel is used
CATCH_STEPS = 60 // MINUTES_PER_STEP
FLAME_STEPS = 4 * 60 // MINUTES_PER_STEP
EMBERS_AT = 0.5

# heat of each state, multiplies p_burn in spread.py
HEAT_OF_STATE = np.zeros(states.NUM_STATES)
HEAT_OF_STATE[states.BURNING_STATES] = 1


def heat_of(state_grid):
    # capyle puts -100 round the edge, clip it to 0 so it has no heat
    return HEAT_OF_STATE[np.clip(state_grid, 0, None).astype(int)]


def update(grid, burning, fuel, fuel_start):
    """Put each burning cell in the right stage"""
    steps_burnt = fuel_start - fuel
    used = steps_burnt / np.maximum(fuel_start, 1)
    flame_over = steps_burnt >= CATCH_STEPS + FLAME_STEPS
    grid[burning & (steps_burnt >= CATCH_STEPS)] = states.FLAMING
    grid[burning & flame_over] = states.SMOULDERING
    grid[burning & flame_over & (used >= EMBERS_AT)] = states.EMBERS
