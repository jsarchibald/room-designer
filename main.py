import numpy as np
import pygame
from pyleap.leap import getLeapInfo, getLeapFrame
from screeninfo import get_monitors
from sys import argv
import threading

import events
from graphics import grid, gridSpace, messageCenter, roomObject
from speech import listen

# Allow for windowed and full-screen modes
monitor_1 = get_monitors()[0]
if len(argv) > 1 and argv[1] == "w":
    SCREEN_DIMS = [1024, 768]
    GRID_PX_DIMS = [768, 768]
    window_const = pygame.RESIZABLE
else:
    SCREEN_DIMS = [monitor_1.width, monitor_1.height]
    GRID_PX_DIMS = [monitor_1.height, monitor_1.height]
    window_const = pygame.FULLSCREEN

# Space dimensions of grid
GRID_DIMS = [20, 20]

# Open window
pygame.init()
screen = pygame.display.set_mode(SCREEN_DIMS, window_const)
pygame.display.set_caption("Room Designer")

# Start grid, loops for input
done = False
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

roomGrid = grid(GRID_DIMS[0], GRID_DIMS[1], GRID_PX_DIMS[0], GRID_PX_DIMS[1], True)
messageCenter = messageCenter(GRID_PX_DIMS[0] + 10, 10)

listener_thread = threading.Thread(target=listen)
listener_thread.start()

while not done:
    clock.tick(10)

    for event in pygame.event.get():
        # Basic UI events
        if event.type == pygame.QUIT:
            done = True
            messageCenter.setText("Exiting program...")
        if event.type == pygame.VIDEORESIZE and window_const == pygame.RESIZABLE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            SCREEN_DIMS = event.size
            messageCenter.setText("Resizing window.")

        # What to do when waiting for a command to be speech-to-text converted
        if event.type == events.capture_space_type:
            roomGrid.lockSpace()
            messageCenter.setText("Parsing voice command...")
        if event.type == events.done_listening_type:
            messageCenter.setText("Waiting for voice command.")
        if event.type == events.error_type:
            messageCenter.setText(event.error)

        # Creating things
        if event.type == events.create_type:
            location = event.location
            print(event)
            if event.location[0] < 0:
                location = roomGrid.lockedSpace
            if event.shape == "circle":
                obj = roomObject(event.color,
                                 circle=roomGrid.getCoords(location, True) + [roomGrid.spaceDims[0] // 2],
                                 outline=event.outline)
                roomGrid.addObject(obj)
            elif event.shape == "rectangle":
                rect = roomGrid.getCoords(location)
                rect = rect[:2] + [event.size[0] * roomGrid.spaceDims[0], event.size[1] * roomGrid.spaceDims[1]]
                obj = roomObject(event.color, rect=rect, outline=event.outline)
                roomGrid.addObject(obj)

    screen.fill((255, 255, 255))
    
    messageCenter.draw(screen)
    roomGrid.draw(screen)

    # Leap motion controller
    info = getLeapInfo()
    if info.connected:
        hand = getLeapFrame().hands[0]
        #x_window = int(np.interp(hand.palm_pos[0], [-150, 150], [0, GRID_PX_DIMS[0]]))
        #y_window = int(np.interp(hand.palm_pos[1], [100, 350], [GRID_PX_DIMS[1], 0]))
        x_grid = int(np.interp(hand.palm_pos[0], [-150, 150], [0, GRID_DIMS[0] - 1]))
        y_grid = int(np.interp(hand.palm_pos[1], [100, 350], [GRID_DIMS[1] - 1, 0]))

        roomGrid.highlight((x_grid, y_grid), True)

    pygame.display.flip()

pygame.quit()