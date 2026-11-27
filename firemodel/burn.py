"""p_burn = P0 * p_veg * density, based on Freire & DaCamara (2019)"""

import numpy as np

from . import terrain_map, states
from .settings import MINUTES_PER_STEP


P0 = 0.04

# chaparral, forest, canyon, lake. p_veg multiplies p_burn: forest is hard to
# light, canyon always catches (25 = 1 / P0) and lake never burns
P_VEG = np.array([1, 0.25, 25, 0])

HOUR = 60 // MINUTES_PER_STEP
DAY = 24 * HOUR

# burn time in steps: chaparral 3 days, forest 10 days, canyon 10 hours
BURN_TIME = np.array([3 * DAY, 10 * DAY, 10 * HOUR, 0])


def make_cells(density_noise_map, terrain=None):
    # terrain can be passed in when the map has been changed (extra forest)
    if terrain is None:
        terrain = terrain_map.make_map()
    p_burn = np.clip(P0 * (P_VEG[terrain]) * density_noise_map, 0, 1)
    # based on values from the paper
    fuel = BURN_TIME[terrain].copy() * density_noise_map
    return {'p_burn': p_burn,
            'fuel': fuel,
            'fuel_start': fuel.copy(),
            'burnt_as': states.BURNT_STATE_OF_TERRAIN[terrain]}
