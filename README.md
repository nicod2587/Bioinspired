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

`python firemodel/terrain_map.py` saves a picture of the map to `screenshots/`.

## Code

Model is split up in `firemodel/` so we can each work on a different file:

- `terrain_map.py` - the map and cell size
- `burn.py` - p_burn (Freire & DaCamara) and burn times
- `heat.py` - burn stages (heat is all 1 for now)
- `spread.py` - fire spread, p_burn x heat x wind per neighbour
- `wind.py` - wind (no wind until the wind branch is merged)
- `states.py` - states and colours
- `settings.py` - time step

`ca_descriptions/forest_fire.py` is the capyle file that uses them. Ignition point and number of steps are set there.

## Settings

200m cells (250x250), 20 min steps, 1200 steps = 400 hours. A run takes about 40s and 600MB. With no wind the fire from the power plant gets to the town after about 400 steps (130 hours).
