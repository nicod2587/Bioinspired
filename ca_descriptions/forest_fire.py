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

# states
UNBURNT = 0
BURNING = 1
BURNT = 2

# grid is 100x100 so each cell is 0.5km x 0.5km of the 50km x 50km map
GRID_DIMS = (100, 100)

# one terrain type for now
IGNITION_PROB = 0.3  # chance per burning neighbour per step of catching fire
BURN_TIME = 5        # steps a cell burns for before it burns out


def transition_func(grid, neighbourstates, neighbourcounts, fuel):
    # unpack state counts for state 0, 1 and 2
    unburnt_neighbours, burning_neighbours, burnt_neighbours = neighbourcounts
    # each burning neighbour gets its own chance to light the cell
    ignite_prob = 1 - (1 - IGNITION_PROB) ** burning_neighbours
    catches_fire = (grid == UNBURNT) & (np.random.random(grid.shape) < ignite_prob)
    # burning cells use up a step of fuel, and burn out when it runs out
    burning = grid == BURNING
    fuel[burning] -= 1
    burns_out = burning & (fuel <= 0)
    grid[catches_fire] = BURNING
    grid[burns_out] = BURNT
    return grid


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    # ---THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED---
    config.title = "Forest fire"
    config.dimensions = 2
    config.states = (UNBURNT, BURNING, BURNT)
    # ------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    # green = unburnt, orange = burning, dark grey = burnt
    config.state_colors = [(0.2, 0.6, 0.2), (1, 0.5, 0), (0.15, 0.15, 0.15)]
    config.num_generations = 300
    config.grid_dims = GRID_DIMS
    # no wrapping, otherwise fire leaving one edge comes back on the other
    config.wrap = False
    # fire starts in the top left corner (power plant)
    initial_grid = np.full(GRID_DIMS, UNBURNT)
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

    # fuel left in each cell, counted in steps of burning
    fuel = np.full(config.grid_dims, BURN_TIME)

    # Create grid object, passing fuel through to the transition function
    grid = Grid2D(config, (transition_func, fuel))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
