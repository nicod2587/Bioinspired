"""Turns the last gui run into a gif, capyle saves every run to temp/timeline.pkl"""

# py make_gif.py [out.gif] [steps per frame] [scale]
# default: results/fire.gif, one frame per hour, 5 px per cell

import os
import pickle
import sys

import numpy as np
from PIL import Image, ImageDraw

from firemodel import states, settings

HERE = os.path.dirname(os.path.abspath(__file__))
TIMELINE = os.path.join(HERE, 'temp', 'timeline.pkl')
CONFIG = os.path.join(HERE, 'temp', 'config.pkl')


def run_settings():
    # settings the gui run used, falls back to settings.py
    for sub in ['capyle', 'capyle/ca', 'capyle/guicomponents']:
        sys.path.append(os.path.join(HERE, sub))
    import capyle.ca  # noqa: F401, has to come before unpickling the config
    with open(CONFIG, 'rb') as f:
        return {**settings.current(), **getattr(pickle.load(f), 'settings', {})}


def main():
    minutes = run_settings()['MINUTES_PER_STEP']
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'results', 'fire.gif')
    every = int(sys.argv[2]) if len(sys.argv) > 2 else 60 // minutes
    scale = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    with open(TIMELINE, 'rb') as f:
        timeline = np.asarray(pickle.load(f))

    # drop the frames after the fire has gone out
    burning = [states.is_burning(g).any() for g in timeline]
    last = min(max(i for i, b in enumerate(burning) if b) + 1 if any(burning) else 0,
               len(timeline) - 1)
    frames_idx = list(range(0, last + 1, every))
    if frames_idx[-1] != last:
        frames_idx.append(last)

    # paletted images keep the gif small, state number = palette index
    # plus an extra white entry for the label
    palette = [int(round(c * 255)) for rgb in states.COLOURS for c in rgb] + [255] * 3
    white = states.NUM_STATES
    frames = []
    for i in frames_idx:
        img = Image.fromarray(timeline[i].astype(np.uint8), mode='P')
        img.putpalette(palette)
        img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
        hours = i * minutes / 60
        ImageDraw.Draw(img).text((4, 2), 'day %d  %02d:00' % (hours // 24, hours % 24),
                                 fill=white)
        frames.append(img)

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=60, loop=0, optimize=False)
    print('saved %d frames (steps 0-%d of %d) to %s'
          % (len(frames), last, len(timeline) - 1, out))


if __name__ == '__main__':
    main()
