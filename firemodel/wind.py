"""Wind multiplier for each neighbour direction. TODO - on the wind branch"""

import numpy as np
import math

WIND_SPEED = 8.0      # m/s
WIND_FROM_DEG = 0     # direction it blows from, 0 = N, 90 = E

CONSTANT_1=0.05
CONSTANT_2=0.13

# (row, col), NW N NE W E SW S SE
NEIGHBOUR_OFFSETS = [(-1, -1), (-1, 0), (-1, 1),
                     (0, -1),           (0, 1),
                     (1, -1),  (1, 0),  (1, 1)]


def spread_factors(speed=WIND_SPEED, from_deg=WIND_FROM_DEG):
    return np.ones(len(NEIGHBOUR_OFFSETS))


def spread_chance(propagation_direction):
    theta = WIND_FROM_DEG - propagation_direction
    chance = math.exp(WIND_SPEED * (CONSTANT_1 + CONSTANT_2 * (math.cos(math.radians(theta)) - 1) ))
    return chance