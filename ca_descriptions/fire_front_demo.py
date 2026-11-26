# Name: Fire front demo
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

from capyle.ca import Grid2D
import capyle.utils as utils
import numpy as np

# small demo of the burn stages for the heat slide, not the real map
UNBURNT, CATCHING, FLAMING, SMOULDERING, EMBERS, BURNT = range(6)

# same colours as firemodel/states.py
COLOURS = [(0.76, 0.75, 0.15),   # unburnt chaparral
           (0.85, 0.20, 0.05),   # catching
           (1.00, 0.85, 0.25),   # flaming
           (0.50, 0.10, 0.05),   # smouldering
           (0.30, 0.10, 0.10),   # embers
           (0.20, 0.20, 0.15)]   # burnt

HEAT = np.array([0, 0.3, 1, 0.05, 0.01, 0])
P_BURN = 0.25

# steps until each stage ends (counted from catching)
CATCH_END = 1
FLAME_END = 4
SMOULDER_END = 14
EMBER_END = 24


def transition_func(grid, neighbourstates, neighbourcounts, age):
    burning = (grid >= CATCHING) & (grid <= EMBERS)
    age[burning] += 1

    # each burning neighbour gets its own go at lighting the cell
    not_lit = np.ones(grid.shape)
    for n in neighbourstates:
        heat = HEAT[np.clip(n, 0, None).astype(int)]
        not_lit *= 1 - P_BURN * heat
    lit = (grid == UNBURNT) & (np.random.random(grid.shape) > not_lit)

    grid[burning & (age >= CATCH_END)] = FLAMING
    grid[burning & (age >= FLAME_END)] = SMOULDERING
    grid[burning & (age >= SMOULDER_END)] = EMBERS
    grid[burning & (age >= EMBER_END)] = BURNT
    grid[lit] = CATCHING
    return grid


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    # ---THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED---
    config.title = "Fire front demo"
    config.dimensions = 2
    config.states = tuple(range(6))
    # ------------------------------------------------------------------------

    config.state_colors = COLOURS
    config.grid_dims = (40, 60)
    config.wrap = False
    initial_grid = np.zeros(config.grid_dims, int)
    initial_grid[:3, :3] = FLAMING   # lit in the top left corner
    config.initial_grid = initial_grid

    if len(args) == 2:
        config.num_generations = 60
        config.save()
        sys.exit()

    return config


def main():
    config = setup(sys.argv[1:])
    age = np.zeros(config.grid_dims)
    age[:3, :3] = CATCH_END
    grid = Grid2D(config, (transition_func, age))
    timeline = grid.run()
    config.save()
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
