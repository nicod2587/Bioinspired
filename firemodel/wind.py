"""Wind multiplier for each neighbour direction. TODO - on the wind branch"""

import numpy as np


WIND_SPEED = 0.0      # m/s
WIND_FROM_DEG = 0     # direction it blows from, 0 = N, 90 = E

# (row, col), NW N NE W E SW S SE
NEIGHBOUR_OFFSETS = [(-1, -1), (-1, 0), (-1, 1),
                     (0, -1),           (0, 1),
                     (1, -1),  (1, 0),  (1, 1)]


def spread_factors(speed=WIND_SPEED, from_deg=WIND_FROM_DEG):
    return np.ones(len(NEIGHBOUR_OFFSETS))
