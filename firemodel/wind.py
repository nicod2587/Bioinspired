"""Wind multiplier for each neighbour direction, from Alexandridis et al. (2008)"""

import numpy as np
import math

from .settings import WIND_SPEED, WIND_FROM_DEG

# paper (Alexandridis 2008) uses 0.045 and 0.131, too weak on our grid
CONSTANT_1=0.15
CONSTANT_2=0.2


def spread_chance(propagation_direction):
    # theta = angle between the wind and the way the fire is spreading.
    # with the wind cos = 1 so it's exp(V * C1), against it cos = -1 and
    # it's exp(V * (C1 - 2 * C2)), less than 1
    theta = WIND_FROM_DEG - propagation_direction
    chance = math.exp(WIND_SPEED * (CONSTANT_1 + CONSTANT_2 * (math.cos(math.radians(theta)) - 1) ))
    return chance