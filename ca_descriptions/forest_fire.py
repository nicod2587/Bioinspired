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
#   p_burn = p0 * (1 + p_veg) * (1 + p_den) * p_w * p_s
# Wind (p_w) and slope (p_s) are left out for now.

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

# OUR CHOICE: Freire & DaCamara use 100m cells and 20 minute steps, but at that
# scale the brief's burn times (days) last hundreds of steps and the whole fire
# is one solid burning block. 0.5km cells (100x100 is the full 50km x 50km map,
# town is 5x5 cells) with longer steps keeps burn times to a sensible number
# of steps. Each step is 2 hours.
GRID_DIMS = (100, 100)
MINUTES_PER_STEP = 120

# Freire & DaCamara base burning probability is 0.58. OUR CHOICE: lowered,
# at 0.5km cells 0.58 makes spread near-certain in every direction and the
# fire front goes square.
P0 = 0.2

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
# one step, but the brief gives a burn time for each terrain. Our reading of it:
#   canyon "several hours" = 6 hours, chaparral "several days" = 3 days,
#   forest "up to one month" = 30 days
BURN_TIME = np.array([3 * 24 * 60, 30 * 24 * 60, 6 * 60, 0]) // MINUTES_PER_STEP


def transition_func(grid, neighbourstates, neighbourcounts, p_burn, fuel):
    # unpack state counts for state 0, 1, 2 and 3
    unburnt_neighbours, burning_neighbours, burnt_neighbours, non_burnable_neighbours = neighbourcounts
    # rule 4: each burning neighbour gets its own chance p_burn to light the cell
    ignite_prob = 1 - (1 - p_burn) ** burning_neighbours
    catches_fire = (grid == UNBURNT) & (np.random.random(grid.shape) < ignite_prob)
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
    # burning probability and fuel of every cell, fixed by the terrain
    p_burn = np.clip(P0 * (1 + P_VEG[terrain]) * (1 + P_DEN[terrain]), 0, 1)
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
