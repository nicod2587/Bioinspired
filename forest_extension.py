"""Q4: where should 25 km2 (100 cells) of extra dense forest go? North wind, both ignitions"""

# py forest_extension.py [runs], saves results/forest_extension.csv/png

import csv
import os
import sys
from multiprocessing import Pool

import numpy as np

import experiments as ex
from firemodel import terrain_map, states, burn, wind, density, settings, forest

MAX_HOURS = 168
N = terrain_map.GRID_SIZE


def strip(rows, cols):
    mask = np.zeros((N, N), dtype=bool)
    mask[rows, cols] = True
    return mask


def town_shield():
    # the L forest's bottom arm grown south towards the town
    mask = strip(slice(70, 84), slice(36, 43))
    mask[84, 38:40] = True
    return mask


# every layout is 100 cells joined onto existing forest
LAYOUTS = {'none': None,
           'corridor': strip(slice(62, 66), slice(50, 75)),     # forest arm to the lake
           'town shield': town_shield(),                        # forest arm towards the town
           'north-east block': strip(slice(30, 34), slice(65, 90)),  # north-east forest grown south
           'top strip': strip(slice(10, 14), slice(50, 75)),    # top strip grown east
           'west gap': strip(slice(60, 70), slice(0, 10)),      # forest arm to the west edge of the map
           'split': strip(slice(62, 67), slice(0, 10)) | strip(slice(62, 64), slice(50, 75))}  # 50 in each gap


def make_terrain(name):
    terrain = terrain_map.make_map()
    if LAYOUTS[name] is not None:
        terrain, note = forest.extend(terrain, LAYOUTS[name])
        assert not note, name + ': ' + note
    return terrain


def hours_to_town(job):
    name, ignition, seed = job[:3]
    np.random.seed(seed)
    # job can have a 4th item, the wind direction, otherwise north
    wind.WIND_FROM_DEG, wind.WIND_SPEED = (job[3] if len(job) > 3 else 0), settings.WIND_SPEED
    terrain = make_terrain(name)
    cells = burn.make_cells(density.generate_noise_map(terrain_map.GRID_DIMS), terrain)
    cells['directions'] = ex.BEARINGS
    grid = terrain_map.draw_states(terrain)
    grid[ex.IGNITIONS[ignition]] = states.FLAMING
    town = terrain_map.town_mask()
    for step in range(1, MAX_HOURS * 60 // settings.MINUTES_PER_STEP + 1):
        grid = ex.transition_func(grid, ex.neighbour_states(grid), None, cells)
        if states.has_caught(grid[town]).any():
            return step * settings.MINUTES_PER_STEP / 60
        if not states.is_burning(grid).any():
            return None
    return None


def main(runs):
    names = list(LAYOUTS)
    igs = list(ex.IGNITIONS)
    jobs = [(n, ig, s) for n in names for ig in igs for s in range(runs)]
    with Pool() as pool:
        hours = pool.map(hours_to_town, jobs)
    res = {(n, ig): [MAX_HOURS if h is None else h for (m, i, _), h in zip(jobs, hours) if m == n and i == ig]
           for n in names for ig in igs}

    os.makedirs(os.path.join(ex.HERE, 'results'), exist_ok=True)
    with open(os.path.join(ex.HERE, 'results', 'forest_extension.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['layout', 'ignition', 'run', 'hours_to_town'])
        for (n, ig), hs in res.items():
            for i, h in enumerate(hs):
                writer.writerow([n, ig, i, round(h, 2)])
    print('%d runs each, north wind %g m/s, median hours to town (change vs no extra forest)' % (runs, settings.WIND_SPEED))
    for n in names:
        print('  %-17s' % n + ''.join('  %s %5.1f h (%+.1f)' % (ig, np.median(res[n, ig]),
              np.median(res[n, ig]) - np.median(res['none', ig])) for ig in igs))

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    fig = plt.figure(figsize=(16, 7.6))
    w = 0.98 / len(names)
    for k, n in enumerate(names):
        ax = fig.add_axes([0.01 + k * w, 0.50, w * 0.92, 0.38])
        grid = terrain_map.draw_states(make_terrain(n))
        new = (make_terrain(n) == terrain_map.FOREST) & (terrain_map.make_map() != terrain_map.FOREST)
        ax.imshow(grid, cmap=ListedColormap(states.COLOURS), vmin=0, vmax=states.NUM_STATES - 1,
                  interpolation='nearest')
        ax.contour(new, levels=[0.5], colors='white', linewidths=1.5)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title('no extra forest' if n == 'none' else n, fontsize=12)
    for k, ig in enumerate(igs):
        ax = fig.add_axes([0.1 + k * 0.5, 0.08, 0.31, 0.33])
        y = np.arange(len(names))[::-1]
        rng = np.random.default_rng(0)
        for yi, n in zip(y, names):
            h = np.array(res[n, ig])
            ax.scatter(h, yi + rng.uniform(-0.25, 0.25, len(h)), s=12, alpha=0.6, edgecolors='none',
                       color='grey' if n == 'none' else '#3f6626')
            med = np.median(h)
            ax.plot([med, med], [yi - 0.38, yi + 0.38], color='black', lw=2.5)
            ax.text(1.01, yi, '%.1f h (%+.1f)' % (med, med - np.median(res['none', ig])), va='center',
                    fontsize=10, transform=ax.get_yaxis_transform())
        ax.set_yticks(y, ['no extra forest' if n == 'none' else n for n in names])
        ax.set_title('fire from the %s' % ig, fontsize=12)
        ax.set_xlabel('hours until the fire reaches the town (dots = runs, line = median)')
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Q4: where to add 25 km2 (100 cells) of dense forest, north wind %g m/s, new forest outlined in white'
                 % settings.WIND_SPEED, fontsize=13)
    fig.savefig(os.path.join(ex.HERE, 'results', 'forest_extension.png'), dpi=150, facecolor='white')


def wind_sweep(runs, names=('none', 'west gap', 'corridor', 'split')):
    # does the layout still help when the wind comes from somewhere else
    igs = list(ex.IGNITIONS)
    dirs = list(ex.DIRECTIONS)
    jobs = [(n, ig, s, ex.DIRECTIONS[d]) for n in names for ig in igs for d in dirs for s in range(runs)]
    with Pool() as pool:
        hours = pool.map(hours_to_town, jobs)
    med = {}
    for n in names:
        for ig in igs:
            for d in dirs:
                hs = [MAX_HOURS if h is None else h for j, h in zip(jobs, hours)
                      if j[0] == n and j[1] == ig and j[3] == ex.DIRECTIONS[d]]
                med[n, ig, d] = np.median(hs)
    with open(os.path.join(ex.HERE, 'results', 'forest_extension_wind.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['layout', 'ignition', 'wind_from', 'median_hours_to_town'])
        for (n, ig, d), h in med.items():
            writer.writerow([n, ig, d, round(h, 1)])
    print('%d runs each, median hours to town (%d = never got there)' % (runs, MAX_HOURS))
    for ig in igs:
        print(ig)
        print('  %-10s' % '' + ''.join('%7s' % d for d in dirs))
        for n in names:
            print('  %-10s' % n + ''.join('%7.1f' % med[n, ig, d] for d in dirs))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'wind':
        wind_sweep(int(sys.argv[2]) if len(sys.argv) > 2 else 10)
    else:
        main(int(sys.argv[1]) if len(sys.argv) > 1 else 30)
