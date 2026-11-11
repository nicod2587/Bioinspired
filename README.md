# COM3524 forest fire CA

Group project code. Built on CAPyLE, the CA tool from the week 5 lab.

## Setup

```
conda env create -f environment_COM3524.yml
conda activate COM3524
```

## Running

```
python main.py
```

or `run.bat` (Windows) / `run.sh` (Mac/Linux). On Windows without conda, `py main.py` works if `python` opens the Microsoft Store. In the GUI go to File > Open, pick `forest_fire.py` from `ca_descriptions/` and click "Apply configuration & run CA".

To see the map on its own: `python firemodel/terrain_map.py` saves `screenshots/terrain_map.png`.

## Code layout

The model is in `firemodel/`, one file per part, so we can each work on our own file:

| File | What's in it |
|---|---|
| `firemodel/terrain_map.py` | The map from the brief and its colours. Cell size (`CELL_KM`) is here. |
| `firemodel/burn.py` | Burn formula (`p_burn`, Freire & DaCamara) and burn times. |
| `firemodel/heat.py` | Burn stages and heat. Placeholder: every burning stage counts as heat 1 for now. |
| `firemodel/spread.py` | How fire passes to a cell: `p_burn x heat x wind` for each of the 8 neighbours. |
| `firemodel/wind.py` | Wind factor for each direction. Placeholder (no wind) until the `wind` branch is merged. |
| `firemodel/states.py` | State numbers and colours. New states go here. |
| `firemodel/settings.py` | Time step. |
| `ca_descriptions/forest_fire.py` | The CAPyLE file. Puts the parts together; set the ignition point and number of steps here. |

Each step (`transition_func` in `forest_fire.py`):

1. `spread.catches_fire` works out which unburnt cells catch fire
2. burning cells use a step of fuel and `heat.update` moves them to the right burn stage
3. cells with no fuel left become burnt
4. newly lit cells start as `CATCHING`

## Current settings

- 200 m cells (250 x 250), 20 minutes per step, 1200 steps (400 hours). A run takes about 40 s and 600 MB.
- No wind. A fire from the power plant reaches the town after about 400 steps (130 hours).
