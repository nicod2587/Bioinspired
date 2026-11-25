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

or `run.bat` / `run.sh`. On Windows use `py main.py` if `python` just opens the Microsoft Store. Then File > Open, pick `ca_descriptions/forest_fire.py` and click "Apply configuration & run CA".

`python -m firemodel.terrain_map` saves a picture of the map to `screenshots/`.

## Code

Model is split up in `firemodel/` so we can each work on a different file:

- `settings.py` - things we change between runs (ignition, wind, cell size, generations)
- `terrain_map.py` - the map
- `burn.py` - p_burn (Freire & DaCamara) and burn times
- `heat.py` - burn stages (heat per stage)
- `spread.py` - fire spread, p_burn x heat x wind per neighbour
- `wind.py` - wind, based on Alexandridis et al. (2008)
- `states.py` - states and colours

`ca_descriptions/forest_fire.py` is the capyle file that uses them.

## Settings

500m cells (100x100), 5 min steps, 2880 steps = 10 days. With no wind the fire gets to the town after about 61 hours from the power plant and 47 hours from the incinerator.

## Experiments

```
py experiments.py [runs] [wind speed]
```

Runs the model without the gui for every wind direction from both ignition points and saves the time until the fire reaches the town to `results/` (csv and a chart). Default is 10 runs each at the wind speed in `settings.py`.
