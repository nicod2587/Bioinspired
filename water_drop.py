"""Q3: where should the 12.5 km2 water drop go? Fire from the incinerator, northerly wind"""

# py water_drop.py [runs]   compares the tactics in water.PLANS, saves results/water_tactics.csv/png
# py water_drop.py scan     tries every position of a line and a square (slow)

import csv
import os
import sys
from multiprocessing import Pool

import numpy as np

import experiments as ex
from firemodel import terrain_map, states, burn, wind, density, settings, water

MAX_HOURS = 168


def hours_to_town(job):
    # one run with the given water mask (None = no drop)
    name, mask, seed = job
    np.random.seed(seed)
    wind.WIND_FROM_DEG, wind.WIND_SPEED = 0, settings.WIND_SPEED
    terrain = terrain_map.make_map()
    cells = burn.make_cells(density.generate_noise_map(terrain_map.GRID_DIMS))
    cells['directions'] = ex.BEARINGS
    if mask is not None:
        water.add_to_cells(cells, water.plan_from_mask(mask), terrain)
    grid = terrain_map.draw_states(terrain)
    grid[terrain_map.INCINERATOR] = states.FLAMING
    town = terrain_map.town_mask()
    for step in range(1, MAX_HOURS * 60 // settings.MINUTES_PER_STEP + 1):
        grid = ex.transition_func(grid, ex.neighbour_states(grid), None, cells)
        if states.has_caught(grid[town]).any():
            return step * settings.MINUTES_PER_STEP / 60
        if not states.is_burning(grid).any():
            return None
    return None


def scan(shape, rows, cols, seeds):
    # every placement of one shape, returns mean hours (a week if never reached)
    jobs = [((r, c), water.line(r, c) if shape == 'line' else water.block(r, c), s)
            for r in rows for c in cols for s in seeds]
    with Pool() as pool:
        hours = pool.map(hours_to_town, jobs, chunksize=8)
    table = {}
    for (rc, _, _), h in zip(jobs, hours):
        table.setdefault(rc, []).append(MAX_HOURS if h is None else h)
    return {rc: np.mean(hs) for rc, hs in table.items()}


NAMES = {'none': 'no drop', 'early': 'early attack', 'corridor': 'corridor line',
         'town': 'town ring', 'head': 'follow the head'}


def snapshot(name, hours, seed=2):
    # the grid after some hours, for the picture
    np.random.seed(seed)
    wind.WIND_FROM_DEG, wind.WIND_SPEED = 0, settings.WIND_SPEED
    terrain = terrain_map.make_map()
    cells = burn.make_cells(density.generate_noise_map(terrain_map.GRID_DIMS))
    cells['directions'] = ex.BEARINGS
    if name != 'none':
        water.add_to_cells(cells, water.plan_from_mask(water.PLANS[name]()), terrain)
    grid = terrain_map.draw_states(terrain)
    grid[terrain_map.INCINERATOR] = states.FLAMING
    for _ in range(hours * 60 // settings.MINUTES_PER_STEP):
        grid = ex.transition_func(grid, ex.neighbour_states(grid), None, cells)
    return grid


def compare_tactics(runs):
    names = list(NAMES)
    jobs = [(n, None if n == 'none' else water.PLANS[n](), s) for n in names for s in range(runs)]
    with Pool() as pool:
        hours = pool.map(hours_to_town, jobs)
        snaps = pool.starmap(snapshot, [(n, 24) for n in names])
    results = {n: [MAX_HOURS if h is None else h for (m, _, _), h in zip(jobs, hours) if m == n] for n in names}

    os.makedirs(os.path.join(ex.HERE, 'results'), exist_ok=True)
    with open(os.path.join(ex.HERE, 'results', 'water_tactics.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['tactic', 'run', 'hours_to_town'])
        for n in names:
            for i, h in enumerate(results[n]):
                writer.writerow([n, i, round(h, 2)])
    base = np.mean(results['none'])
    print('%d runs each, incinerator fire, north wind %g m/s' % (runs, settings.WIND_SPEED))
    for n in names:
        print('  %-16s %5.1f +- %3.1f h  (%+.1f h)' % (NAMES[n], np.mean(results[n]), np.std(results[n]),
                                                    np.mean(results[n]) - base))

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    fig = plt.figure(figsize=(15, 6.2))
    for i, n in enumerate(names):
        ax = fig.add_axes([0.01 + i * 0.198, 0.40, 0.18, 0.5])
        ax.imshow(snaps[i], cmap=ListedColormap(states.COLOURS), vmin=0, vmax=states.NUM_STATES - 1,
                  interpolation='nearest')
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title('%s, 24 h' % NAMES[n], fontsize=12)
    ax = fig.add_axes([0.25, 0.08, 0.5, 0.25])
    # every run as a dot, so the lucky runs show up, black line = median
    y = np.arange(len(names))[::-1]
    rng = np.random.default_rng(0)
    for yi, n in zip(y, names):
        h = np.array(results[n])
        ax.scatter(h, yi + rng.uniform(-0.25, 0.25, len(h)), s=14, alpha=0.6,
                   color='grey' if n == 'none' else '#3a6fb0', edgecolors='none')
        med = np.median(h)
        ax.plot([med, med], [yi - 0.38, yi + 0.38], color='black', lw=2.5)
        ax.text(81, yi, 'median %.1f h (%+.1f)' % (med, med - np.median(results['none'])),
                va='center', fontsize=10)
    ax.set_yticks(y, [NAMES[n] for n in names])
    ax.set_xlabel('hours until the fire reaches the town (each dot is one of %d runs, line = median)' % runs)
    ax.set_xlim(20, 80)
    ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Q3: water drop tactics, 2 cells (0.5 km2) an hour from 2 h, incinerator fire, north wind %g m/s'
                 % settings.WIND_SPEED, fontsize=13)
    fig.savefig(os.path.join(ex.HERE, 'results', 'water_tactics.png'), dpi=150, facecolor='white')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'scan':
        seeds = range(5)
        with Pool() as pool:
            base = pool.map(hours_to_town, [('none', None, s) for s in range(20)])
        base = [MAX_HOURS if h is None else h for h in base]
        lines = scan('line', range(0, 99, 2), range(0, 76, 3), seeds)
        blocks = scan('block', range(0, 94, 3), range(0, 94, 3), seeds)
        np.save(os.path.join(ex.HERE, 'results', 'water_scan.npy'),
                {'base': base, 'lines': lines, 'blocks': blocks}, allow_pickle=True)
    else:
        compare_tactics(int(sys.argv[1]) if len(sys.argv) > 1 else 30)
