# Name: Shape test
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

# test map to see what shape the fire makes, not the real map. same rules as
# forest_fire.py. left third dense forest, middle third chaparral, right third
# a random cell-by-cell mix of the two (capyle's randomise2d)

import numpy as np

from capyle.ca import Grid2D, randomise2d
import capyle.utils as utils

from firemodel import terrain_map, states, burn, heat, spread, wind

GRID_DIMS = (100, 300)          # rows, cols. 0.5 km cells = 50 x 150 km
THIRD = GRID_DIMS[1] // 3
FOREST_SHARE = 0.5              # share of forest in the mixed third
IGNITIONS = [(50, THIRD // 2), (50, THIRD + THIRD // 2), (50, 2 * THIRD + THIRD // 2)]
NUM_GENERATIONS = 600           # 50 h

# wind blowing south (from the north). 180 = blowing north
wind.WIND_FROM_DEG = 0
wind.WIND_SPEED = 8.0


def make_terrain():
    terrain = np.full(GRID_DIMS, terrain_map.CHAPARRAL)
    terrain[:, :THIRD] = terrain_map.FOREST
    # capyle loads the file again on run, so fix the seed to get the same mix,
    # then reseed so the fire itself is still random
    np.random.seed(1)
    terrain[:, 2 * THIRD:] = randomise2d(terrain[:, 2 * THIRD:].copy(), terrain_map.CHAPARRAL,
                                         [(terrain_map.FOREST, FOREST_SHARE)])
    np.random.seed(None)
    return terrain


TERRAIN = make_terrain()


def transition_func(grid, neighbourstates, neighbourcounts, cells):
    catches_fire = spread.catches_fire(grid, neighbourstates,
                                       cells['p_burn'], cells['directions'])
    burning = states.is_burning(grid)
    cells['fuel'][burning] -= 1
    heat.update(grid, burning, cells['fuel'], cells['fuel_start'])
    burns_out = burning & (cells['fuel'] <= 0)
    grid[burns_out] = cells['burnt_as'][burns_out]
    grid[catches_fire] = states.CATCHING
    return grid


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    # ---THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED---
    config.title = "Shape test"
    config.dimensions = 2
    config.states = tuple(range(states.NUM_STATES))
    # ------------------------------------------------------------------------

    config.state_colors = states.COLOURS
    config.grid_dims = GRID_DIMS
    config.wrap = False
    # draw_states is fixed to the real map size, so draw this one here (no town)
    initial_grid = np.where(TERRAIN == terrain_map.FOREST, terrain_map.DRAW_FOREST,
                            terrain_map.DRAW_CHAPARRAL)
    # 3x3 square of catching cells at each ignition point
    for r, c in IGNITIONS:
        initial_grid[r - 1:r + 2, c - 1:c + 2] = states.CATCHING
    config.initial_grid = initial_grid

    if len(args) == 2:
        config.num_generations = NUM_GENERATIONS
        config.save()
        sys.exit()

    return config


def main():
    config = setup(sys.argv[1:])
    terrain = TERRAIN
    fuel = burn.BURN_TIME[terrain].astype(float)
    cells = {'p_burn': burn.P0 * burn.P_VEG[terrain],
             'fuel': fuel,
             'fuel_start': fuel.copy(),
             'burnt_as': states.BURNT_STATE_OF_TERRAIN[terrain],
             # capyle order NW N NE W E SW S SE
             'directions': [315, 0, 45, 270, 90, 225, 180, 135]}

    grid = Grid2D(config, (transition_func, cells))
    timeline = grid.run()

    config.save()
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
