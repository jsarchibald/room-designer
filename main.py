import numpy as np
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame
from pyleap.leap import getLeapInfo, getLeapFrame
from sys import argv
import threading
import tkinter as tk

import events
from handle_events import handle_event
from graphics import grid, gridSpace, messageCenter, roomObject
from settings import SCREEN_DIMS, GRID_PX_DIMS, WINDOW_CONST, GRID_DIMS, LEAP_THRESHOLD
from speech import listen

def main():
    """The main program loop."""
    # Open window
    pygame.init()
    icon = pygame.image.load("img/icon_32.png")
    pygame.display.set_icon(icon)
    screen = pygame.display.set_mode(SCREEN_DIMS, WINDOW_CONST)
    pygame.display.set_caption("Room Designer - New room")

    # Start grid, loops for input
    done = False
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)

    roomGrid = grid(GRID_DIMS[0], GRID_DIMS[1], GRID_PX_DIMS[0], GRID_PX_DIMS[1], True)
    mc = messageCenter(GRID_PX_DIMS[0] + 10, 10)

    # Start speech recognition thread
    listener_thread = threading.Thread(target=listen, args=[roomGrid])
    listener_thread.daemon = True
    listener_thread.start()

    # Loading screen icon, so the listener thread has a second to start listening
    screen.fill((255, 255, 255))
    icon = pygame.image.load("img/icon_512.png")
    
    # Font for loading screen
    font = pygame.font.Font("fonts/Roboto-Regular.ttf", 24)

    # Tell user about ESC to close program in full screen (since no [X] button)
    if WINDOW_CONST == pygame.FULLSCREEN:
        text_surface = font.render("Press ESC to close, if voice commands fail.", 1, (0, 0, 0))
        text_size = text_surface.get_size()
        coords = ((SCREEN_DIMS[0] - text_size[0]) // 2, (SCREEN_DIMS[1] - 64))
        screen.blit(text_surface, coords)

    # Alert user if there's no Leap connection
    info = getLeapInfo()
    if not info.connected:
        text_surface = font.render("Could not connect to the Leap Motion Controller.", 1, (0, 0, 0))
        text_size = text_surface.get_size()
        coords = ((SCREEN_DIMS[0] - text_size[0]) // 2, (SCREEN_DIMS[1] - 128))
        screen.blit(text_surface, coords)

    screen.blit(icon, ((SCREEN_DIMS[0] - 512) // 2, (SCREEN_DIMS[1] - 512) // 2))
    pygame.display.flip()

    pygame.time.wait(3000)

    # Animation loop
    while not done:
        clock.tick(10)

        for event in pygame.event.get():
            res = handle_event(event, mc, roomGrid)
            if type(res) == bool:
                done = res
            elif type(res) == tuple:
                if type(res[0]) == grid:
                    roomGrid = res[0]
                    listener_thread = res[1]

        screen.fill((255, 255, 255))
        
        mc.draw(screen)
        roomGrid.draw(screen)

        # Leap motion controller
        info = getLeapInfo()
        if info.connected:
            hand = getLeapFrame().hands[0]
            x_grid = int(np.interp(hand.palm_pos[0], [-150, 150], [0, GRID_DIMS[0] - 1]))
            y_grid = int(np.interp(hand.palm_pos[1], [100, 350], [GRID_DIMS[1] - 1, 0]))
            
            roomGrid.highlight((x_grid, y_grid), True)
            
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
