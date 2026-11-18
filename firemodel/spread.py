"""Each neighbour has a p_burn * heat * wind chance of lighting the cell."""

import numpy as np

from . import heat, states


def catches_fire(grid, neighbourstates, p_burn, wind_factors):
    chance_not_lit = np.ones(grid.shape)
    # both in capyle's order: NW N NE W E SW S SE
    for direction in range(8):
        neighbour_heat = heat.heat_of(neighbourstates[direction])
        p = np.clip(p_burn * neighbour_heat * wind_factors[direction], 0, 1)
        chance_not_lit *= 1 - p
    lit = np.random.random(grid.shape) > chance_not_lit
    return states.is_unburnt(grid) & lit
