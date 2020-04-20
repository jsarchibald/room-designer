import numpy as np
import pygame
from pyleap.leap import getLeapInfo, getLeapFrame
import threading

import events
from graphics import grid, gridSpace, roomObject
from speech import listen

SCREEN_DIMS = [1280, 720]
GRID_DIMS = [20, 20]

pygame.init()
screen = pygame.display.set_mode(SCREEN_DIMS, pygame.FULLSCREEN)
pygame.display.set_caption("Room Designer")

done = False
clock = pygame.time.Clock()

roomGrid = grid(GRID_DIMS[0], GRID_DIMS[1], SCREEN_DIMS[0], SCREEN_DIMS[1])

listener_thread = threading.Thread(target=listen)
listener_thread.start()

while not done:
    clock.tick(10)
     
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == events.capture_space_type:
            roomGrid.lockSpace()
        if event.type == events.what_space_type:
            print(roomGrid.lockedSpace)

    screen.fill((255, 255, 255))
    
    roomGrid.draw(screen)

    info = getLeapInfo()
    if info.connected:
        hand = getLeapFrame().hands[0]
        hand_x = hand.palm_pos[0]
        x = int(np.interp(hand.palm_pos[0], [-150, 150], [0, GRID_DIMS[0] - 1]))
        y = int(np.interp(hand.palm_pos[1], [100, 350], [GRID_DIMS[1] - 1, 0]))

        roomGrid.highlight((x, y), True)

    pygame.display.flip()

pygame.quit()