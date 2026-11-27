"""Aerial water drop (Q3). 12.5 km2 of water = 50 cells at 0.5 km.

Planes start at DROP_HOUR and drop CELLS_PER_HOUR cells every hour, in the
order of the plan, until all 50 are used.
- water on an unburnt cell: it gets a water buffer like the fuel. wet (blue)
  for the first WET_HOURS, then damp (a darker version of the terrain). it
  can't catch fire until the water is gone, then it goes back to normal
- every step the water dries like the catching code works:
    water lost = 1 + FIRE_DRYING * sum of the heat of the 8 neighbours
  so a fire next to a wet cell dries it much faster
- water on a burning cell: the fire is put out and the cell can never burn again
- water on a burnt cell is wasted
"""

import numpy as np

from . import terrain_map, states, heat
from .settings import MINUTES_PER_STEP, CELL_KM, WATER_START_HOUR, WATER_CELLS_PER_HOUR

N = terrain_map.GRID_SIZE
TOWN_ROWS, TOWN_COLS = terrain_map.TOWN_ROWS, terrain_map.TOWN_COLS
MAX_CELLS = int(round(12.5 / CELL_KM ** 2))    # 50
HOUR = 60 // MINUTES_PER_STEP

DROP_HOUR = WATER_START_HOUR    # first plane over the fire, set in settings.py
CELLS_PER_HOUR = WATER_CELLS_PER_HOUR    # cells of water the planes drop each hour
WET_HOURS = 1
DAMP_HOURS = 23

# extra water lost per step for each unit of heat from a burning neighbour
FIRE_DRYING = 2


def line(row, col, length=25, thick=2):
    # horizontal strip, 25 x 2 cells = 12.5 km x 1 km
    mask = np.zeros((N, N), dtype=bool)
    mask[row:row + thick, col:col + length] = True
    return mask


def block(row, col, size=7):
    # square, 7 x 7 = 49 cells = 3.5 x 3.5 km
    mask = np.zeros((N, N), dtype=bool)
    mask[row:row + size, col:col + size] = True
    return mask


def town_ring():
    # ring round the town, then more rings on the north side until 50 cells
    rows, cols = terrain_map.TOWN_ROWS, terrain_map.TOWN_COLS
    mask = np.zeros((N, N), dtype=bool)
    mask[rows.start - 1:rows.stop + 1, cols.start - 1:cols.stop + 1] = True
    mask[rows.start - 2, cols.start - 3:cols.stop + 3] = True
    mask[rows.start - 3, cols.start - 4:cols.stop + 4] = True
    mask[terrain_map.town_mask()] = False
    return mask


# a few fixed plans, positions from the scan in water_drop.py
PLANS = {'early': lambda: line(6, 75),       # across the fire just south of the incinerator
         'corridor': lambda: line(64, 42),   # gap between the forest and the lake
         'town': town_ring,                  # ring round the town
         'head': lambda: 'head'}             # each hour, just in front of the fire nearest the town


def plan_from_mask(mask, start=terrain_map.INCINERATOR):
    # drop order: the cells closest to the fire first
    if isinstance(mask, str):
        return mask
    rows, cols = np.where(mask)
    order = np.argsort((rows - start[0]) ** 2 + (cols - start[1]) ** 2)
    return list(zip(rows[order], cols[order]))


def head_targets(grid, count):
    # unburnt cells touching the fire, the ones closest to the town first
    burning = states.is_burning(grid)
    near_fire = np.zeros_like(burning)
    padded = np.pad(burning, 1)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            near_fire |= padded[1 + dr:1 + dr + N, 1 + dc:1 + dc + N]
    rows, cols = np.where(near_fire & states.is_unburnt(grid))
    town_r = (TOWN_ROWS.start + TOWN_ROWS.stop) / 2
    town_c = (TOWN_COLS.start + TOWN_COLS.stop) / 2
    order = np.argsort((rows - town_r) ** 2 + (cols - town_c) ** 2)[:count]
    return list(zip(rows[order], cols[order]))


def add_to_cells(cells, plan, terrain):
    # plan = cells in the order they get dropped, or 'head' to pick them each
    # hour from where the fire is. water on lakes is not used
    if plan != 'head':
        plan = [rc for rc in plan if terrain[rc] != terrain_map.LAKE]
        assert len(plan) <= MAX_CELLS, 'too much water: %d cells' % len(plan)
    cells['water_plan'] = plan
    cells['unburnt_as'] = terrain_map.draw_states(terrain)
    cells['water_left'] = np.zeros(terrain.shape)
    cells['step'] = 0
    return cells


def drop(grid, cells, rc):
    if states.is_burning(grid[rc]):
        grid[rc] = states.EXTINGUISHED
    elif states.is_unburnt(grid[rc]) or grid[rc] == states.WET or np.isin(grid[rc], states.DAMP_STATE_OF_DRAW):
        grid[rc] = states.WET
        cells['water_left'][rc] = (WET_HOURS + DAMP_HOURS) * HOUR


def update(grid, neighbourstates, cells):
    # called once per step from the transition function
    if 'water_plan' not in cells:
        return grid
    cells['step'] += 1
    step = cells['step']
    # every hour from DROP_HOUR the next few cells of the plan get dropped.
    # HOUR = 12 steps, so this is true on steps 24, 36, 48... when DROP_HOUR = 2
    if step >= DROP_HOUR * HOUR and (step - DROP_HOUR * HOUR) % HOUR == 0:
        # how many cells were already dropped in the hours before this one
        done = (step - DROP_HOUR * HOUR) // HOUR * CELLS_PER_HOUR
        if cells['water_plan'] == 'head':
            targets = head_targets(grid, CELLS_PER_HOUR) if done < MAX_CELLS else []
        else:
            targets = cells['water_plan'][done:done + CELLS_PER_HOUR]
        for rc in targets:
            drop(grid, cells, rc)
    # wet and damp cells dry out, faster next to the fire
    left = cells['water_left']
    drying = left > 0
    if drying.any():
        fire_heat = np.zeros(grid.shape)
        for direction in range(8):
            fire_heat += heat.heat_of(neighbourstates[direction])
        loss = 1 + FIRE_DRYING * fire_heat
        left[drying] -= loss[drying]
    # wet -> damp once the first hour of water is used up
    to_damp = drying & (grid == states.WET) & (left <= DAMP_HOURS * HOUR)
    grid[to_damp] = states.DAMP_STATE_OF_DRAW[cells['unburnt_as'][to_damp]]
    # water all gone, back to the normal unburnt state
    dry = drying & (left <= 0)
    grid[dry] = cells['unburnt_as'][dry]
    return grid
