# Name: Forest fire
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, CAConfig, randomise2d
import capyle.utils as utils
import numpy as np

# Spread rules follow Freire & DaCamara (2019), "Using cellular automata to
# simulate wildfire propagation and to assist in fire management", NHESS 19.
# Their burning probability is
#   p_burn = p0 * (1 + p_veg) * (1 + p_den) * p_w
# (slope term dropped, our map is flat)

# states (Freire & DaCamara's four cell states)
UNBURNT = 0
BURNING = 1
BURNT = 2
NON_BURNABLE = 3

# terrain types
CHAPARRAL = 0
FOREST = 1
CANYON = 2
LAKE = 3

# grid is 100x100 so each cell is 0.5km x 0.5km of the 50km x 50km map
GRID_DIMS = (100, 100)

# Freire & DaCamara constants
# OUR CHOICE: their p0 is 0.58, tuned for 100m cells and 20 minute steps. Ours
# are 500m cells, so at 0.58 spread saturates (probability ~1 in the wind
# direction) and the fire front goes square. 0.2 keeps the front ragged and
# lets wind stretch it. Needs justifying/tuning, see notes.
P0 = 0.2
C1 = 0.045
C2 = 0.131

# p_veg and p_den per terrain, values from Freire & DaCamara Table 1:
#   chaparral -> shrubland (0.4), normal density (0)
#   canyon    -> shrubland (0.4), dense (0.3), the brief says it ignites very easily
#   lake      -> no vegetation (-1, -1), so it can never burn
#   forest    -> OUR CHOICE: their table rates forest at 0.4, but the brief says
#                dense forest doesn't ignite easily, so we use their -0.4 value
#                with dense (0.3)
P_VEG = np.array([0.4, -0.4, 0.4, -1])
P_DEN = np.array([0, 0.3, 0.3, -1])

# OUR ADDITION: steps a cell burns for. Freire & DaCamara burn every cell for
# one step. Placeholder ratios from the brief, 1 step = 6 hours:
#   canyon several hours, chaparral several days, forest up to a month
BURN_TIME = np.array([12, 120, 1, 0])

# wind, placeholders until we pick values
WIND_SPEED = 5       # m/s
WIND_FROM = 0        # compass degrees the wind blows from, 0 = northerly

# neighbour offsets (row, col) in the order Grid2D gives neighbourstates
NEIGHBOUR_OFFSETS = [(-1, -1), (-1, 0), (-1, 1),
                     (0, -1),           (0, 1),
                     (1, -1),  (1, 0),  (1, 1)]


def wind_factor(row_offset, col_offset):
    """p_w for fire spreading from the neighbour at this offset into the cell"""
    # spread direction as (east, north), from the neighbour to the cell
    spread = np.array([-col_offset, row_offset], dtype=float)
    spread /= np.linalg.norm(spread)
    # direction the wind blows towards
    towards = np.radians(WIND_FROM + 180)
    wind = np.array([np.sin(towards), np.cos(towards)])
    cos_theta = spread.dot(wind)
    return np.exp(WIND_SPEED * (C1 + C2 * (cos_theta - 1)))


def transition_func(grid, neighbourstates, neighbourcounts, p_burn, fuel):
    # rule 4: each burning neighbour can spread fire into an unburnt cell
    # with probability p_burn for that direction
    no_spread = np.ones(grid.shape)
    for direction, neighbour in enumerate(neighbourstates):
        burning_neighbour = neighbour == BURNING
        no_spread[burning_neighbour] *= 1 - p_burn[direction][burning_neighbour]
    catches_fire = (grid == UNBURNT) & (np.random.random(grid.shape) < 1 - no_spread)
    # rule 2 (with fuel): burning cells use up a step of fuel and are
    # completely burnt when it runs out
    burning = grid == BURNING
    fuel[burning] -= 1
    burns_out = burning & (fuel <= 0)
    # rules 1 and 3: non-burnable and burnt cells never change
    grid[catches_fire] = BURNING
    grid[burns_out] = BURNT
    return grid


def make_terrain():
    """Terrain type of every cell, one type of land for now"""
    return np.full(GRID_DIMS, CHAPARRAL)


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    # ---THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED---
    config.title = "Forest fire"
    config.dimensions = 2
    config.states = (UNBURNT, BURNING, BURNT, NON_BURNABLE)
    # ------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    # green = unburnt, orange = burning, dark grey = burnt, blue = lake
    config.state_colors = [(0.2, 0.6, 0.2), (1, 0.5, 0), (0.15, 0.15, 0.15), (0.2, 0.4, 0.9)]
    config.num_generations = 300
    config.grid_dims = GRID_DIMS
    # no wrapping, otherwise fire leaving one edge comes back on the other
    config.wrap = False
    # lakes are non-burnable, fire starts in the top left corner (power plant)
    terrain = make_terrain()
    initial_grid = np.full(GRID_DIMS, UNBURNT)
    initial_grid[terrain == LAKE] = NON_BURNABLE
    initial_grid[0, 0] = BURNING
    config.initial_grid = initial_grid

    # ----------------------------------------------------------------------

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main():
    # Open the config object
    config = setup(sys.argv[1:])

    terrain = make_terrain()
    # p_burn for each of the 8 spread directions, worked out once
    # as terrain and wind don't change during a run
    p_veg_den = P0 * (1 + P_VEG[terrain]) * (1 + P_DEN[terrain])
    p_burn = np.array([np.clip(p_veg_den * wind_factor(*offset), 0, 1)
                       for offset in NEIGHBOUR_OFFSETS])
    # fuel left in each cell, counted in steps of burning
    fuel = BURN_TIME[terrain].copy()

    # Create grid object, passing p_burn and fuel through to the transition function
    grid = Grid2D(config, (transition_func, p_burn, fuel))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
