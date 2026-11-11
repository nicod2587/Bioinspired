"""How fire spreads to a cell.

Each of the 8 neighbours has a chance of p_burn * heat * wind to light the
cell. The cell catches fire unless they all fail.
"""

import numpy as np

from . import heat, states


def catches_fire(grid, neighbourstates, p_burn, wind_factors):
    """True for unburnt cells that catch fire this step"""
    chance_not_lit = np.ones(grid.shape)
    # neighbourstates and wind_factors are both in the order NW N NE W E SW S SE
    for direction in range(8):
        neighbour_heat = heat.heat_of(neighbourstates[direction])
        p = np.clip(p_burn * neighbour_heat * wind_factors[direction], 0, 1)
        chance_not_lit *= 1 - p
    lit = np.random.random(grid.shape) > chance_not_lit
    return states.is_unburnt(grid) & lit
