import numpy as np
import pygame
from screeninfo import get_monitors
from sys import argv


# Essentially global variables.
# Allow for windowed and full-screen modes
monitor_1 = get_monitors()[0]
if len(argv) > 1 and argv[1] == "f":
    SCREEN_DIMS = [monitor_1.width, monitor_1.height]
    GRID_PX_DIMS = [monitor_1.height, monitor_1.height]
    WINDOW_CONST = pygame.FULLSCREEN
elif len(argv) > 1 and argv[1] == "w":
    SCREEN_DIMS = [1024, 768]
    GRID_PX_DIMS = [768, 768]
    WINDOW_CONST = pygame.RESIZABLE
else:
    fullscreen = input("Open in full screen? y/n: ")
    if fullscreen[0] == "y":
        SCREEN_DIMS = [monitor_1.width, monitor_1.height]
        GRID_PX_DIMS = [monitor_1.height, monitor_1.height]
        WINDOW_CONST = pygame.FULLSCREEN
    else:
        SCREEN_DIMS = [1024, 768]
        GRID_PX_DIMS = [768, 768]
        WINDOW_CONST = pygame.RESIZABLE
    

# Space dimensions of grid
GRID_DIMS = [20, 20]

# Speech credentials file path
SPEECH_CRED_FILE = "../../Dropbox/College/2019-2020/6.835/Project/6835-95e43858e35a.json"

# Leap smoothing
LEAP_THRESHOLD = np.sqrt((GRID_PX_DIMS[0] // GRID_DIMS[0]) ** 2 + (GRID_PX_DIMS[1] // GRID_DIMS[1]) ** 2)
