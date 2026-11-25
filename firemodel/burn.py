"""p_burn = P0 * (1 + p_veg) * (1 + p_den), from Freire & DaCamara (2019)"""

import numpy as np

from . import terrain_map, states
from .settings import MINUTES_PER_STEP


P0 = 0.12

# chaparral, forest, canyon, lake. from Freire & DaCamara table 1 except
# forest is -0.4 (brief says it's hard to light) and lake is -1 (never burns)
P_VEG = np.array([1, 0.2, 100, 0])

HOUR = 60 // MINUTES_PER_STEP
DAY = 24 * HOUR

# burn time in steps: chaparral 3 days, forest 10 days, canyon 10 hours
BURN_TIME = np.array([3 * DAY, 10 * DAY, 10 * HOUR, 0])


def make_cells(density_noise_map):
    terrain = terrain_map.make_map()
    p_burn = np.clip(P0 * (P_VEG[terrain]) * density_noise_map, 0, 1)
    # based on values from the paper
    fuel = BURN_TIME[terrain].copy() * density_noise_map
    return {'p_burn': p_burn,
            'fuel': fuel,
            'fuel_start': fuel.copy(),
            'burnt_as': states.BURNT_STATE_OF_TERRAIN[terrain]}
