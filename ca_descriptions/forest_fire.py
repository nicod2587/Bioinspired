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

import numpy as np

from capyle.ca import Grid2D
import capyle.utils as utils

<<<<<<< HEAD
from firemodel import settings
# apply the gui's settings panel before the rest of the model reads settings
if __name__ == '__main__' and len(sys.argv) > 1:
    settings.override(getattr(utils.load(sys.argv[1]), 'settings', {}))
from firemodel import terrain_map, states, burn, heat, spread, wind, density
=======
from firemodel import terrain_map, states, burn, heat, spread, wind, density, settings, label, water, forest
>>>>>>> 66f540679bef40ef47f5fd9992607d315a010a41


GRID_DIMS = terrain_map.GRID_DIMS

IGNITION = {'power plant': terrain_map.POWER_PLANT,
            'incinerator': terrain_map.INCINERATOR}[settings.IGNITION]
NUM_GENERATIONS = settings.NUM_GENERATIONS
TOWN = terrain_map.town_mask()


class StopAtTown(Grid2D):
    # same as capyle's run loop but stops as soon as a town cell catches fire
    reached_at = None

    def _runca(self, num_generations, progressbar, timeline):
        timeline[0] = np.copy(self.grid)
        for i in range(num_generations):
            self.step()
            timeline[i + 1] = np.copy(self.grid)
            if settings.STOP_AT_VILLAGE and states.has_caught(self.grid[TOWN]).any():
                self.reached_at = i + 1
                break
            # copied from capyle, only updates the progress bar every 10 steps
            if (i + 1) % 10 == 9:
                progressbar.set(i + 1)
        # closes the progress window
        progressbar.set(num_generations)


def transition_func(grid, neighbourstates, neighbourcounts, cells):
    grid = water.update(grid, neighbourstates, cells)
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
    config.settings = settings.current()
    config.setting_choices = settings.CHOICES
    config.grid_dims = GRID_DIMS
    config.wrap = False
    # water cells painted in the initial grid editor (state 13, light blue)
    painted = config.initial_grid
    drawn = np.zeros(GRID_DIMS, dtype=bool)
    if painted is not None and np.shape(painted) == GRID_DIMS:
        drawn = np.asarray(painted) == states.WET
    terrain = terrain_map.make_map()
    if settings.FOREST_EXTENSION and painted is not None and np.shape(painted) == GRID_DIMS:
        # forest painted in the editor, only the first 100 painted are used and
        # bits that don't join onto the existing forest are removed
        new_forest = (np.asarray(painted) == terrain_map.DRAW_FOREST) & (terrain != terrain_map.FOREST)
        order = [(int(r), int(c)) for r, c in getattr(config, 'paint_order', [])]
        # no order saved (e.g. a drawing from before) = keep the cells nearest the forest
        terrain, note = forest.extend(terrain, new_forest, order or None)
        if note:
            print(note)
    initial_grid = terrain_map.draw_states(terrain)
    initial_grid[IGNITION] = states.FLAMING
    initial_grid[drawn] = states.WET
    config.initial_grid = initial_grid

    # ----------------------------------------------------------------------

    # only set on load so the gui box isn't overwritten on run
    if len(args) == 2:
        config.num_generations = NUM_GENERATIONS
        config.save()
        sys.exit()

    return config


def main():
    # Open the config object
    config = setup(sys.argv[1:])
    noise_map = density.generate_noise_map(config.grid_dims)
    if density.DENSITY:
        density.show_noise_map(noise_map)
    # the map with any extra forest from setup
    # main() runs separately from setup(), so the extra forest is read back
    # from the initial grid setup() made
    terrain = terrain_map.make_map()
    terrain[config.initial_grid == terrain_map.DRAW_FOREST] = terrain_map.FOREST
    cells = burn.make_cells(noise_map, terrain)
    drawn = config.initial_grid == states.WET
    plan = None
    if settings.WATER_DROP and not drawn.any():
        print('water drop is on but no water was painted, so none is dropped')
    if settings.WATER_DROP and drawn.any():
        # painted water: dropped a few cells an hour in the order they were painted
        usable = drawn & (terrain != terrain_map.LAKE)
        # a cell painted again later moves to its latest place in the order,
        # painted cells with no order (older drawings) go last, nearest the fire first
        # dict keeps only the last time each cell was painted, then sort by that
        painted_at = {(int(r), int(c)): i for i, (r, c) in enumerate(getattr(config, 'paint_order', []))}
        plan = sorted((rc for rc in painted_at if usable[rc]), key=painted_at.get)
        plan += [rc for rc in water.plan_from_mask(usable, IGNITION) if rc not in painted_at]
        if len(plan) > water.MAX_CELLS:
            print('painted %d water cells, only the first %d painted are used'
                  % (len(plan), water.MAX_CELLS))
            plan = plan[:water.MAX_CELLS]
    if plan is not None:
        water.add_to_cells(cells, plan, terrain)
    # the painted cells only mark the plan, the run starts from the plain map
    config.initial_grid = np.where(drawn, terrain_map.draw_states(terrain), config.initial_grid)
    # bearing of each neighbour, capyle order is NW N NE W E SW S SE
    cells['directions'] = [
        315, 0, 45, 270, 90, 225, 180, 135
    ]

    # Create grid object
    grid = StopAtTown(config, (transition_func, cells))
    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()
    if settings.SHOW_CLOCK:
        # only drawn on the saved frames, the run itself never sees it
        steps_per_hour = 60 // settings.MINUTES_PER_STEP
        for i, frame in enumerate(timeline):
            if frame is not None:
                label.write(frame, ['%dh' % (i // steps_per_hour)], states.TEXT,
                            terrain_map.DRAW_TOWN, corner='bottom', tiny=True)
    if grid.reached_at is not None:
        # cut off the unused steps and write the time on the last frame
        timeline = timeline[:grid.reached_at + 1]
        hours = grid.reached_at * settings.MINUTES_PER_STEP / 60
        text = ['Village reached', 'in %d hours' % round(hours), '(%d steps)' % grid.reached_at]
        label.write(timeline[-1], text, states.TEXT, terrain_map.DRAW_TOWN)

    # save updated config to file. the water is cleared, so draw it again each run
    config.paint_order = []
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
