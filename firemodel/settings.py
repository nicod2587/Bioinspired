"""Things we change between runs, all in one place"""

# where the fire starts: 'power plant' or 'incinerator'
IGNITION = 'power plant'

# default for the generations box in the gui, 2880
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

# stop the run when the fire reaches the village and show the time on the map
STOP_AT_VILLAGE = True

# small clock in the bottom right corner showing the hours since the fire started
SHOW_CLOCK = True

# water drop on/off. paint up to 50 cells with state 13 (light blue) in the
# initial grid editor before each run, they're dropped in the order painted
WATER_DROP = True

# hour the first water is dropped, then WATER_CELLS_PER_HOUR cells an hour until all 50 are used
WATER_START_HOUR = 2
WATER_CELLS_PER_HOUR = 2

# extra dense forest on/off. paint up to 100 cells with state 1 (forest) in the
# initial grid editor, it has to join onto the existing forest
FOREST_EXTENSION = True
