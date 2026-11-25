"""Runs the model without the gui and times how long the fire takes to reach the town"""

# py experiments.py [runs] [wind speed], saves a csv and a chart to results/

import csv
import os
import runpy
import sys
from multiprocessing import Pool

import numpy as np

from firemodel import terrain_map, states, burn, wind, settings

# use the same transition function as the gui
HERE = os.path.dirname(os.path.abspath(__file__))
transition_func = runpy.run_path(os.path.join(HERE, 'ca_descriptions', 'forest_fire.py'),
                                 run_name='experiments')['transition_func']

RUNS = 10
MAX_HOURS = 168   # give up after a week

IGNITIONS = {'power plant': terrain_map.POWER_PLANT,
             'incinerator': terrain_map.INCINERATOR}
DIRECTIONS = {'N': 0, 'NE': 45, 'E': 90, 'SE': 135,
              'S': 180, 'SW': 225, 'W': 270, 'NW': 315}

# same as forest_fire.py, capyle order NW N NE W E SW S SE
BEARINGS = [315, 0, 45, 270, 90, 225, 180, 135]
OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def neighbour_states(grid):
    # capyle uses -100 off the edge of the grid
    padded = np.pad(grid, 1, constant_values=-100)
    rows, cols = grid.shape
    return np.array([padded[1 + dr:1 + dr + rows, 1 + dc:1 + dc + cols]
                     for dr, dc in OFFSETS])


def hours_to_town(job):
    # one run, hours until the town catches fire (None if it never does)
    ignition, wind_from, speed, seed = job
    np.random.seed(seed)
    wind.WIND_FROM_DEG = wind_from
    wind.WIND_SPEED = speed
    cells = burn.make_cells()
    cells['directions'] = BEARINGS
    grid = terrain_map.draw_states(terrain_map.make_map())
    grid[IGNITIONS[ignition]] = states.FLAMING
    town = terrain_map.town_mask()
    for step in range(1, MAX_HOURS * 60 // settings.MINUTES_PER_STEP + 1):
        grid = transition_func(grid, neighbour_states(grid), None, cells)
        if (grid[town] >= states.CATCHING).any():
            return step * settings.MINUTES_PER_STEP / 60
        if not states.is_burning(grid).any():
            return None
    return None


def plot(summary, speed, runs, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    colours = {'power plant': 'tab:blue', 'incinerator': 'tab:orange'}
    names = list(DIRECTIONS)
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for i, ignition in enumerate(IGNITIONS):
        offset = (i - 0.5) * 0.38
        for j, d in enumerate(names):
            mean, sd, reached = summary[ignition, d]
            if reached == 0:
                ax.text(x[j] + offset, 3, 'x', ha='center', color='grey', fontsize=11)
                continue
            ax.bar(x[j] + offset, mean, 0.34, color=colours[ignition])
            ax.errorbar(x[j] + offset, mean, sd, color='grey', lw=1, capsize=3)
            if reached < runs:
                ax.text(x[j] + offset, mean + sd + 3, '%d/%d' % (reached, runs),
                        ha='center', fontsize=8, color='grey')
    handles = [plt.Rectangle((0, 0), 1, 1, color=colours[k]) for k in IGNITIONS]
    ax.legend(handles, list(IGNITIONS), frameon=False)
    ax.set_xticks(x, ['from ' + n for n in names])
    ax.set_ylabel('hours until fire reaches town')
    ax.set_title('Time to reach the town by wind direction (%g m/s, %d runs each)\n'
                 'x = never reached within %d h, n/%d = runs that reached it'
                 % (speed, runs, MAX_HOURS, runs), fontsize=10)
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', color='lightgrey', lw=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)


def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else RUNS
    speed = float(sys.argv[2]) if len(sys.argv) > 2 else settings.WIND_SPEED
    jobs = [(ig, deg, speed, seed) for ig in IGNITIONS
            for deg in DIRECTIONS.values() for seed in range(runs)]
    with Pool() as pool:
        hours = pool.map(hours_to_town, jobs)

    os.makedirs(os.path.join(HERE, 'results'), exist_ok=True)
    name = 'wind_sweep' if speed == settings.WIND_SPEED else 'wind_sweep_%gms' % speed
    with open(os.path.join(HERE, 'results', name + '.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ignition', 'wind_from', 'wind_speed', 'run', 'hours_to_town'])
        for (ig, deg, sp, seed), h in zip(jobs, hours):
            label = [k for k, v in DIRECTIONS.items() if v == deg][0]
            writer.writerow([ig, label, sp, seed, '' if h is None else round(h, 2)])

    summary = {}
    print('wind %g m/s, %d runs each, hours to town (mean +- sd, runs that got there)' % (speed, runs))
    for ig in IGNITIONS:
        for label, deg in DIRECTIONS.items():
            got = [h for (i, d, _, _), h in zip(jobs, hours) if i == ig and d == deg and h is not None]
            mean = np.mean(got) if got else 0
            sd = np.std(got) if got else 0
            summary[ig, label] = (mean, sd, len(got))
            print('  %-11s from %-2s  %6.1f +- %4.1f  (%d/%d)' % (ig, label, mean, sd, len(got), runs))
    plot(summary, speed, runs, os.path.join(HERE, 'results', name + '.png'))


if __name__ == '__main__':
    main()
