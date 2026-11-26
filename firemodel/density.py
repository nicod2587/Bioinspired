"""A multipler to the lighting probability based on a perlin noise distributed density map"""

import numpy as np
import matplotlib.pyplot as plt
import noise

from .settings import DENSITY

def apply_noise(x, y):
    return noise.pnoise2(x/10, y/10)

def generate_noise_map(grid_dims):
    if not DENSITY:
        return np.ones(grid_dims)
    X, Y = np.meshgrid(np.arange(grid_dims[0]), np.arange(grid_dims[1]), indexing='ij')
    raw =  np.vectorize(apply_noise)(X, Y)
    raw = raw / np.abs(raw).max()
    # raw is now -1 to 1, so density goes from 0.5 to 1.5 with a mean of about 1
    return 1 + 0.5 * raw

def show_noise_map(noise_map):
    plt.figure()
    plt.imshow(noise_map, cmap='gray', interpolation='none')
    plt.colorbar()
    plt.show(block=False)
    plt.pause(0.001)
 #   plt.savefig('noise_map.png')
    plt.close()