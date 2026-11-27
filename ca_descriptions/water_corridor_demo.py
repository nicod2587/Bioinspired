# Name: Water corridor demo
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

# small demo for the water drop slide, not the real map
# a chaparral corridor between two dense forests, like the far west of our map,
# fire lit at the top, wind from the north.
# paint water (state 2) across the corridor in the custom initial grid editor
CHAPARRAL, FOREST, WATER, CATCHING, FLAMING, SMOULDERING, EMBERS, BURNT = range(8)

# same colours as firemodel/states.py
COLOURS = [(0.76, 0.75, 0.15),   # chaparral
           (0.25, 0.40, 0.15),   # dense forest
           (0.55, 0.80, 1.00),   # water
           (0.85, 0.20, 0.05),   # catching
           (1.00, 0.85, 0.25),   # flaming
           (0.50, 0.10, 0.05),   # smouldering
           (0.30, 0.10, 0.10),   # embers
           (0.20, 0.20, 0.15)]   # burnt

HEAT = np.array([0, 0, 0, 0.3, 1, 0.05, 0.01, 0])
P_BURN = 0.25
# forest is much harder to light, water can't burn
P_VEG = np.array([1, 0.05, 0])

# wind from the north, so a burning cell to the north counts more
# capyle neighbour order is NW N NE W E SW S SE
WIND = np.array([1.5, 2, 1.5, 0.7, 0.7, 0.3, 0.2, 0.3])

# steps until each stage ends (counted from catching)
CATCH_END = 1
FLAME_END = 4
SMOULDER_END = 14
EMBER_END = 24

ROWS, COLS = 50, 30
CORRIDOR = slice(10, 20)


def make_map():
    grid = np.full((ROWS, COLS), FOREST)
    grid[:, CORRIDOR] = CHAPARRAL
    return grid


def transition_func(grid, neighbourstates, neighbourcounts, age, veg):
    burning = (grid >= CATCHING) & (grid <= EMBERS)
    age[burning] += 1

    # each burning neighbour gets its own go at lighting the cell
    not_lit = np.ones(grid.shape)
    for n, w in zip(neighbourstates, WIND):
        heat = HEAT[np.clip(n, 0, None).astype(int)]
        not_lit *= 1 - np.clip(P_BURN * w * heat, 0, 1)
    p = 1 - not_lit
    lit = (grid <= FOREST) & (np.random.random(grid.shape) < p * P_VEG[veg])

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
    config.title = "Water corridor demo"
    config.dimensions = 2
    config.states = tuple(range(8))
    # ------------------------------------------------------------------------

    config.state_colors = COLOURS
    config.grid_dims = (ROWS, COLS)
    config.wrap = False
    # keep any water painted in the editor
    painted = config.initial_grid
    initial_grid = make_map()
    if painted is not None and np.shape(painted) == (ROWS, COLS):
        initial_grid[np.asarray(painted) == WATER] = WATER
    initial_grid[:2, CORRIDOR] = FLAMING   # lit at the top of the corridor
    config.initial_grid = initial_grid

    if len(args) == 2:
        config.num_generations = 80
        config.save()
        sys.exit()

    return config


def main():
    config = setup(sys.argv[1:])
    veg = np.where(make_map() == FOREST, FOREST, CHAPARRAL)
    age = np.zeros(config.grid_dims)
    age[config.initial_grid == FLAMING] = CATCH_END
    grid = Grid2D(config, (transition_func, age, veg))
    timeline = grid.run()
    config.save()
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
