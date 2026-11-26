"""Extra dense forest (Q4). 25 km2 of new forest = 100 cells at 0.5 km.

New forest can only go on chaparral and has to join onto the existing forest,
either directly or through other new forest. Only the first 100 cells painted
are used, then any of those that don't connect are removed.
"""

import numpy as np

from . import terrain_map
from .settings import CELL_KM

MAX_CELLS = int(round(25 / CELL_KM ** 2))    # 100


def grow(mask):
    # mask plus its 8 neighbours
    padded = np.pad(mask, 1)
    rows, cols = mask.shape
    out = np.zeros_like(mask)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            out |= padded[1 + dr:1 + dr + rows, 1 + dc:1 + dc + cols]
    return out


def extend(terrain, painted, order=None):
    # returns the new terrain and a short note about what was removed.
    # order = the cells in the order they were painted, if we have it
    allowed = painted & (terrain == terrain_map.CHAPARRAL) & ~terrain_map.town_mask()
    if order is not None:
        # dict.fromkeys drops repeats but keeps the first time each was painted,
        # cells with no order (an older drawing) go after
        first = [rc for rc in dict.fromkeys(order) if allowed[rc]]
        seen = set(first)
        first += [rc for rc in zip(*np.where(allowed)) if rc not in seen]
        allowed = np.zeros_like(allowed)
        for rc in first[:MAX_CELLS]:
            allowed[rc] = True
    reached = terrain == terrain_map.FOREST
    kept = np.zeros_like(allowed)
    # add new forest ring by ring outwards from the existing forest
    while kept.sum() < MAX_CELLS:
        ring = grow(reached) & allowed & ~kept
        if not ring.any():
            break
        rows, cols = np.where(ring)
        for r, c in list(zip(rows, cols))[:MAX_CELLS - kept.sum()]:
            kept[r, c] = True
        reached = reached | kept
    new_terrain = terrain.copy()
    new_terrain[kept] = terrain_map.FOREST
    note = ''
    if painted.sum() > kept.sum():
        note = ('%d painted forest cells used, %d removed (not joined to existing forest '
                'or over the %d cell limit)' % (kept.sum(), painted.sum() - kept.sum(), MAX_CELLS))
    return new_terrain, note
