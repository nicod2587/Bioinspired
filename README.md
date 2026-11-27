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

or `run.bat` / `run.sh`. On Windows use `py main.py` if `python` just opens the Microsoft Store.

1. File > Open, pick `ca_descriptions/forest_fire.py`.
2. Change anything in the settings panel (see below).
3. Click "Apply configuration & run CA", then Play.

The run stops when the fire reaches the village and the time is written on the last frame.

`python -m firemodel.terrain_map` saves a picture of the map to `screenshots/`.

### Settings panel

Shown at the top left once `forest_fire.py` is loaded. The defaults come from `firemodel/settings.py`.

- ignition - power plant (NW corner) or incinerator (NE corner)
- wind speed (m/s) and wind from deg (direction it blows from, 0 = N, 90 = E)
- density - patchy vegetation density from a noise map
- stop at village - stop the run when the fire reaches the village
- water drop, water start hour, water cells per hour - see below
- forest extension - see below

Cell size (500 m) and step length (5 min) are only in `settings.py`, the rest of the model is calibrated to them.

### Drawing water and forest

Tick "Custom" under Initial grid and click Edit. The editor opens on the map.

- Water drop: paint up to 50 cells (12.5 km2) with state 13 (light blue). Planes drop them in the order you painted them, starting at the water start hour.
- Forest extension: paint up to 100 cells (25 km2) with state 1 (dark green). Only cells that join onto the existing forest are kept.

Click "Save and close", then run. The water has to be painted again for each run.

### Demos

Small maps for the slides, not the real model. Open them the same way.

- `ca_descriptions/fire_front_demo.py` - burn stages spreading from a corner
- `ca_descriptions/water_corridor_demo.py` - fire coming down a corridor between two dense forests. Paint water (state 2) across the corridor in the Custom editor to block it.
- `ca_descriptions/shape_test.py` - open map to check the fire shape the wind makes

## Code

Model is split up in `firemodel/`:

- `settings.py` - things we change between runs
- `terrain_map.py` - the map
- `burn.py` - p_burn (Freire & DaCamara) and burn times
- `heat.py` - burn stages (heat per stage)
- `spread.py` - fire spread, p_burn x heat x wind per neighbour
- `wind.py` - wind, based on Alexandridis et al. (2008)
- `density.py` - vegetation density noise map
- `water.py` - water drop
- `forest.py` - forest extension
- `label.py` - writes the time on the last frame
- `states.py` - states and colours

`ca_descriptions/forest_fire.py` is the CAPyLE file that uses them. We also changed a few CAPyLE files in `capyle/`: the settings panel (`guicomponents/settingsui.py`), the editor starting from the map and remembering paint order (`guicomponents/initialgridwindow.py`), and the layout so the run button fits on a laptop screen.

## Experiments

These run the model without the GUI, using the same transition function, and save a csv and a chart to `results/`.

```
py experiments.py [runs] [wind speed]   # Q1/Q2: time to the town for every wind direction, both ignitions
py water_drop.py [runs]                 # Q3: compares water drop tactics (water.PLANS)
py water_drop.py scan                   # Q3: tries every position of a line and a square (slow)
py forest_extension.py [runs]           # Q4: compares places for the extra forest
py forest_extension.py wind [runs]      # Q4: the same for every wind direction
```

`py make_gif.py [out.gif] [steps per frame] [scale]` turns the last GUI run into a gif (default `results/fire.gif`, one frame per hour).
