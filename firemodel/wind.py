"""Wind. Gives a multiplier for each of the 8 neighbour directions.

Not done yet (see the wind branch), so it's 1 in every direction for now.
"""

import numpy as np


WIND_SPEED = 0.0      # m/s
WIND_FROM_DEG = 0     # where the wind comes from: 0 N, 90 E, 180 S, 270 W

# neighbour offsets (row, col) in capyle's order: NW N NE W E SW S SE
NEIGHBOUR_OFFSETS = [(-1, -1), (-1, 0), (-1, 1),
                     (0, -1),           (0, 1),
                     (1, -1),  (1, 0),  (1, 1)]


def spread_factors(speed=WIND_SPEED, from_deg=WIND_FROM_DEG):
    return np.ones(len(NEIGHBOUR_OFFSETS))
