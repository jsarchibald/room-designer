import pygame
import threading
from tkinter import filedialog

import events
from graphics import grid, gridSpace, messageCenter, roomObject
from settings import SCREEN_DIMS, GRID_PX_DIMS, WINDOW_CONST, GRID_DIMS
from speech import listen

# Some handlers based on event type, to abstract out the process
# of obeying commands.
def change_event(event, messageCenter, roomGrid):
    """Change an object in the room."""

    # Get the grid space we should be using
    location = event.location
    if location[0] >= GRID_DIMS[0] or location[1] >= GRID_DIMS[1]:
        return False
    elif location == [-1, -1]:
        location = roomGrid.lockedSpace
    
    # Change the appropriate object (or at least, our best guess)
    if event.method == "rename":
        roomGrid.renameObject(event.obj_type, location, event.text)
    elif event.method == "delete":
        roomGrid.removeObject(event.obj_type, location)

    return False

def create_event(event, messageCenter, roomGrid):
    """Create an object in the room."""

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
                            text=event.text,
                            textColor=event.text_color,
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
                            text=event.text,
                            textColor=event.text_color,
                            objType=event.obj_type,
                            footprint=location + [w, h])
        roomGrid.addObject(obj)
    
    return False

def file_event(event, messageCenter, roomGrid):
    """Deal with file events, e.g. open, save, new."""
    if event.method == "open":
        # Have to make resizable so file dialog appears
        if WINDOW_CONST == pygame.FULLSCREEN:
            pygame.display.set_mode(SCREEN_DIMS, pygame.RESIZABLE)

        path = filedialog.askopenfilename(title="Choose a file.", filetypes=[("JSON", ".json")], defaultextension=".json")

        if path == "":
            return False

        roomGrid.dead = True
        roomGrid = grid(GRID_DIMS[0], GRID_DIMS[1], GRID_PX_DIMS[0], GRID_PX_DIMS[1], True)
        roomGrid.openFile(path)

        listener_thread = threading.Thread(target=listen, args=[roomGrid])
        listener_thread.daemon = True
        listener_thread.start()

        if WINDOW_CONST == pygame.FULLSCREEN:
            pygame.display.set_mode(SCREEN_DIMS, pygame.FULLSCREEN)

        pygame.display.set_caption("Room Designer - {0}".format(roomGrid.title))

        return roomGrid, listener_thread
    elif event.method == "new":
        roomGrid.dead = True
        roomGrid = grid(GRID_DIMS[0], GRID_DIMS[1], GRID_PX_DIMS[0], GRID_PX_DIMS[1], True)

        listener_thread = threading.Thread(target=listen, args=[roomGrid])
        listener_thread.daemon = True
        listener_thread.start()

        pygame.display.set_caption("Room Designer - {0}".format(roomGrid.title))

        return roomGrid, listener_thread
    elif event.method == "save":
        messageCenter.setText("Saving...")
        roomGrid.saveFile(WINDOW_CONST, SCREEN_DIMS, "__RENAME__")
        pygame.display.set_caption("Room Designer - {0}".format(roomGrid.title))
    elif event.method == "export":
        messageCenter.setText("Exporting...")
        roomGrid.export()

    return False

def finish_waiting(event, messageCenter, roomGrid):
    """Events that happen at the end of some input cycle."""
    if roomGrid.waitFunction[0] == "move":
        location = roomGrid.waitFunction[1]["location"]
        to_location = roomGrid.lockedSpace
        objType = roomGrid.waitFunction[1]["objType"]
        roomGrid.setWaitFunction(None, None)

        roomGrid.moveObject(objType, location, to_location)

    return False

def move_event(event, messageCenter, roomGrid):
    """Move objects around the room."""
    location = event.location
    to_location = event.to_location

    if location[0] >= GRID_DIMS[0] or location[1] >= GRID_DIMS[1] \
        or to_location[0] >= GRID_DIMS[0] or to_location[1] >= GRID_DIMS[1]:
        return False
    elif location == [-1, -1]:
        location = roomGrid.lockedSpace
    
    # If we're waiting for Leap info, we have to...well, wait
    if to_location == [-1, -1]:
        roomGrid.setWaitFunction("move", {"location": location, "objType": event.obj_type})
        messageCenter.setText("Point, and say 'here'.")
    else:
        roomGrid.moveObject(event.obj_type, location, to_location)

    return False

def ui_event(event, messageCenter, roomGrid):
    """Handles basic UI events"""

    # Close program
    if event.type == pygame.QUIT \
       or (WINDOW_CONST == pygame.FULLSCREEN \
           and event.type == pygame.KEYDOWN \
           and event.key == pygame.K_ESCAPE):
        messageCenter.setText("Exiting program...")
        return True
    
    # Resize program
    if event.type == pygame.VIDEORESIZE and WINDOW_CONST == pygame.RESIZABLE:
        messageCenter.setText("Resizing window.")
        screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
        SCREEN_DIMS = event.size
        messageCenter.setText("Waiting for voice command.")

    # My own UI events
    if hasattr(event, "method"):
        if event.method == "capture_space":
            roomGrid.lockSpace()
            messageCenter.setText("Parsing voice command...")
        elif event.method == "done_listening":
            if messageCenter.text == "Parsing voice command...":
                messageCenter.setText("Waiting for voice command.")

    return False


# Handle the events that are passed to us
def handle_event(event, messageCenter, roomGrid):
    """Processes incoming events.
    
    Args:
        event: the Pygame event.
        messageCenter: the messageCenter object of this runtime.
        roomGrid: the roomGrid object of this runtime.

    Returns:
        True, if the program should close. Else returns False, or a new messageCenter and roomGrid.
    """

    # Basic UI events
    if event.type == pygame.QUIT or event.type == pygame.VIDEORESIZE or event.type == pygame.KEYDOWN:
        return ui_event(event, messageCenter, roomGrid)

    # New, open, save
    elif event.type == events.file_type:
        return file_event(event, messageCenter, roomGrid)

    # What to do when waiting for a command to be speech-to-text converted
    elif event.type == events.ui_type:
        return ui_event(event, messageCenter, roomGrid)
    
    # Error events
    elif event.type == events.error_type:
        messageCenter.setText(event.error)
        return False

    # Creating things
    elif event.type == events.design_type and event.method == "create":
        return create_event(event, messageCenter, roomGrid)

    # Moving things
    elif event.type == events.design_type and event.method == "move":
        return move_event(event, messageCenter, roomGrid)

    # Finishing two-part commands
    elif event.type == events.ui_type and event.method == "finish_waiting":
        return finish_waiting(event, messageCenter, roomGrid)
    
    # Renaming and deleting things
    elif event.type == events.design_type and event.method in ["rename", "delete"]:
        return change_event(event, messageCenter, roomGrid)
    
    return False
