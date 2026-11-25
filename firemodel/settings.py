"""Things we change between runs, all in one place"""

# where the fire starts: 'power plant' or 'incinerator'
IGNITION = 'power plant'

# default for the generations box in the gui, 2880 = 10 days
NUM_GENERATIONS = 2880

# cell size in km, 0.5 = 100x100. tried 50m and 100m but capyle was too slow
CELL_KM = 0.5

# minutes per step. 5 gives about 1-2.5 km/h in chaparral like real fires
MINUTES_PER_STEP = 5

# wind, 0 speed = no wind
WIND_SPEED = 8.0      # m/s
WIND_FROM_DEG = 0      # direction it blows from, 0 = N, 90 = E

# patchy vegetation density from a noise map, False = same density everywhere
DENSITY = True
DENSITY_IMG_SAVE = False



# shown in the gui's settings panel, NUM_GENERATIONS is the gui's generations box
EDITABLE = ['IGNITION', 'WIND_SPEED', 'WIND_FROM_DEG', 'DENSITY',
            'DENSITY_IMG_SAVE', 'CELL_KM', 'MINUTES_PER_STEP']
CHOICES = {'IGNITION': ['power plant', 'incinerator']}


def current():
    return {name: globals()[name] for name in EDITABLE}


def override(values):
    # has to run before the other firemodel modules import their settings
    for name, value in values.items():
        if name in EDITABLE:
            globals()[name] = value
