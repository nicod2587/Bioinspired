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

from capyle.ca import Grid2D
import capyle.utils as utils

from firemodel import terrain_map, states, burn, heat, spread, wind


GRID_DIMS = terrain_map.GRID_DIMS

IGNITION = terrain_map.POWER_PLANT   # or INCINERATOR

# 20 min steps, so 400 hours. overrides the box in the gui
NUM_GENERATIONS = 1200


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
    config.title = "Forest fire"
    config.dimensions = 2
    config.states = tuple(range(states.NUM_STATES))
    # ------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = states.COLOURS
    config.num_generations = NUM_GENERATIONS
    config.grid_dims = GRID_DIMS
    config.wrap = False
    initial_grid = terrain_map.draw_states(terrain_map.make_map())
    initial_grid[IGNITION] = states.FLAMING
    config.initial_grid = initial_grid

    # ----------------------------------------------------------------------

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main():
    # Open the config object
    config = setup(sys.argv[1:])

    cells = burn.make_cells()
    cells['directions'] = [
        315, 0, 45, 90, 135, 180, 225, 270
    ]

    # Create grid object
    grid = Grid2D(config, (transition_func, cells))
    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
