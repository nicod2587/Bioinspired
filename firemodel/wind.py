"""Wind multiplier for each neighbour direction. TODO - on the wind branch"""

import numpy as np
import math

WIND_SPEED = 30.0      # m/s
WIND_FROM_DEG = -90     # direction it blows from, 0 = N, 90 = E

# taken from paper
CONSTANT_1=0.05
CONSTANT_2=0.13


def spread_chance(propagation_direction):
    theta = WIND_FROM_DEG - propagation_direction
    chance = math.exp(WIND_SPEED * (CONSTANT_1 + CONSTANT_2 * (math.cos(math.radians(theta)) - 1) ))
    return chance