import numpy as np
import pygame
from pyleap.leap import getLeapInfo, getLeapFrame
from screeninfo import get_monitors
from sys import argv
import threading
import tkinter as tk
from tkinter import filedialog

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
icon = pygame.image.load("img/icon_32.png")
pygame.display.set_icon(icon)
screen = pygame.display.set_mode(SCREEN_DIMS, window_const)
pygame.display.set_caption("Room Designer")

root = tk.Tk()
root.withdraw()

# Start grid, loops for input
done = False
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

roomGrid = grid(GRID_DIMS[0], GRID_DIMS[1], GRID_PX_DIMS[0], GRID_PX_DIMS[1], True)
messageCenter = messageCenter(GRID_PX_DIMS[0] + 10, 10)

listener_thread = threading.Thread(target=listen)
listener_thread.daemon = True
listener_thread.start()

# Loading screen icon, so the listener thread has a second to start listening
screen.fill((255, 255, 255))
icon = pygame.image.load("img/icon_512.png")
screen.blit(icon, ((SCREEN_DIMS[0] - 512) // 2, (SCREEN_DIMS[1] - 512) // 2))
pygame.display.flip()

pygame.time.wait(3000)

# Animation loop
while not done:
    clock.tick(10)

    for event in pygame.event.get():
        # Basic UI events
        if event.type == pygame.QUIT:
            done = True
            messageCenter.setText("Exiting program...")
        if event.type == pygame.VIDEORESIZE and window_const == pygame.RESIZABLE:
            messageCenter.setText("Resizing window.")
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            SCREEN_DIMS = event.size
            messageCenter.setText("Waiting for voice command.")

        # New, open, save
        if event.type == events.file_type:
            if event.method == "open":
                # Have to make resizable so file dialog appears
                if window_const == pygame.FULLSCREEN:
                    pygame.display.set_mode(SCREEN_DIMS, pygame.RESIZABLE)

                path = filedialog.askopenfilename(title="Choose a file.", filetypes=[("JSON", ".json")], defaultextension=".json")
                roomGrid.openFile(path)

                if window_const == pygame.FULLSCREEN:
                    pygame.display.set_mode(SCREEN_DIMS, pygame.FULLSCREEN)
            elif event.method == "new":
                roomGrid = grid(GRID_DIMS[0], GRID_DIMS[1], GRID_PX_DIMS[0], GRID_PX_DIMS[1], True)
            elif event.method == "save":
                messageCenter.setText("Saving...")
                roomGrid.saveFile(window_const, SCREEN_DIMS)
                messageCenter.setText("Waiting for voice command.")

        # What to do when waiting for a command to be speech-to-text converted
        if event.type == events.ui_type:
            if event.method == "capture_space":
                roomGrid.lockSpace()
                messageCenter.setText("Parsing voice command...")
            elif event.method == "done_listening":
                messageCenter.setText("Waiting for voice command.")
        
        # Error events
        if event.type == events.error_type:
            messageCenter.setText(event.error)

        # Creating things
        if event.type == events.create_type:
            location = event.location
            if location[0] >= GRID_DIMS[0]:
                location[0] = GRID_DIMS[0] - 1
            if location[1] >= GRID_DIMS[1]:
                location[1] = GRID_DIMS[1] - 1

            footprint = [1, 1]

            if event.location[0] < 0:
                location = roomGrid.lockedSpace
            if event.shape == "circle":
                center = roomGrid.getCoords(location, True)
                radius = [roomGrid.spaceDims[0] // 2]
                obj = roomObject(event.color,
                                 circle=center + radius,
                                 outline=event.outline,
                                 #text="C",
                                 objType=event.obj_type,
                                 footprint=list(location) + [1, 1]) # This needs to be updated if we ever do circles more than one gridspace
                roomGrid.addObject(obj)
            elif event.shape == "rectangle":
                rect = roomGrid.getCoords(location)
                w = min(event.size[0], GRID_DIMS[0] - location[0])
                h = min(event.size[1], GRID_DIMS[1] - location[1])

                # Size should max out based on grid dimensions -- that's handled here
                rect = rect[:2] + [w * roomGrid.spaceDims[0], h * roomGrid.spaceDims[1]]

                obj = roomObject(event.color,
                                 rect=rect,
                                 outline=event.outline,
                                 #text="T",
                                 objType=event.obj_type,
                                 footprint=location + [w, h])
                roomGrid.addObject(obj)

        # Deleting things
        elif event.type == events.delete_type:
            location = event.location
            if location[0] >= GRID_DIMS[0] or location[1] >= GRID_DIMS[1]:
                continue
            elif location == [-1, -1]:
                location = roomGrid.lockedSpace
            
            roomGrid.removeObject(event.obj_type, location)

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