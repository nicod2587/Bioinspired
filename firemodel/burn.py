"""p_burn = P0 * (1 + p_veg) * (1 + p_den), from Freire & DaCamara (2019)"""

import numpy as np

from . import terrain_map, states
from .settings import MINUTES_PER_STEP


P0 = 0.12

# chaparral, forest, canyon, lake. from Freire & DaCamara table 1 except
# forest is -0.4 (brief says it's hard to light) and lake is -1 (never burns)
P_VEG = np.array([0.4, -0.4, 0.4, -1])
P_DEN = np.array([0, 0.3, 0.3, -1])

# burn time in steps: chaparral 3 days, forest 30 days, canyon 6 hours
BURN_TIME = np.array([3 * 24 * 60, 30 * 24 * 60, 6 * 60, 0]) // MINUTES_PER_STEP


def make_cells():
    terrain = terrain_map.make_map()
    p_burn = np.clip(P0 * (1 + P_VEG[terrain]) * (1 + P_DEN[terrain]), 0, 1)
    fuel = BURN_TIME[terrain].copy()
    return {'p_burn': p_burn,
            'fuel': fuel,
            'fuel_start': fuel.copy(),
            'burnt_as': states.BURNT_STATE_OF_TERRAIN[terrain]}
