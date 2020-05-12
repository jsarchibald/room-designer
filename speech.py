import pygame
import speech_recognition as sr
from time import sleep

import events
import objects as obj_types
from settings import SPEECH_CRED_FILE
from speech_helpers import correct_text, either_side, get_after, get_position, get_positions, get_size, is_in_objects, process_relative, select_obj_type

# A variable listing currently-supported commands
COMMANDS = {"create", "save", "add", "insert", "delete", "remove", "goodbye", "exit", "quit", "new", "open", "move", "relocate", "here", "there",  "rename", "export", "right", "left", "up", "down", "resize"}

# Some functions to abstract out the event creation process.
def create(text):
    """Create an object in the room."""

    # Parameters
    location = get_position(text)
    size = get_size(text)

    if "called" in text:
        called = " ".join(get_after("called", text))
    else:
        called = None

    # Object types
    obj = is_in_objects(text)
    if obj is not None:
        obj_type = obj_types.obj_types[obj]
        pygame.event.post(
            pygame.event.Event(events.design_type,
                            method="create",
                            shape=obj_type["shape"],
                            location=location,
                            color=obj_type["color"],
                            size=size,
                            outline=obj_type["outline"],
                            obj_type=obj,
                            text=called,
                            text_color=obj_type["text_color"]))
        

def delete(text):
    """Delete an object in the room."""
    location = get_position(text)
    obj_type = select_obj_type(text)

    # Post event
    evt = pygame.event.Event(events.design_type, method="delete", location=location, obj_type=obj_type)
    pygame.event.post(evt)

def move(text):
    """Move an object in the room."""

    # Parameters
    locations = get_positions(text, 2)
    location = locations[0]

    # Check for relative positioning, then move on to explicit positioning
    to_location = process_relative(text)
    if to_location is None:
        to_location = locations[1]

    obj_type = select_obj_type(text)

    # Post event
    evt = pygame.event.Event(events.design_type,
                             method="move",
                             location=location,
                             to_location=to_location,
                             obj_type=obj_type)
    pygame.event.post(evt)

def rename(text):
    """Rename an object in the scene."""
    # Parameters
    location = get_position(text)

    if "to" in text:
        called = " ".join(get_after("to", text))
    elif "as" in text:
        called = " ".join(get_after("as", text))
    elif "2" in text:
        called = " ".join(get_after("2", text))
    else:
        called = None

    obj_type = select_obj_type(text)

    # Post event
    evt = pygame.event.Event(events.design_type, method="rename", location=location, obj_type=obj_type, text=called)
    pygame.event.post(evt)

def resize(text):
    """Resize an object in the scene."""
    # Parameters
    location = get_position(text)
    size = get_size(text)
    obj_type = select_obj_type(text)

    # Post event
    evt = pygame.event.Event(events.design_type, method="resize", location=location, obj_type=obj_type, size=size)
    pygame.event.post(evt)


# Process individual voice commands.
def process_command(text, roomGrid):
    """Process voice commands. Returns False if program should quit."""
    text = correct_text(text)

    # Program controls
    if "quit" in text or "exit" in text or "close" in text or "goodbye" in text:
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        return False
    elif "open" in text:
        pygame.event.post(events.file_open)
    elif "new" in text and ("design" in text or "room" in text or "file" in text or "project" in text):
        pygame.event.post(events.file_new)
    elif "save" in text:
        pygame.event.post(pygame.event.Event(events.file_type, method="save", change_name=("as" in text)))
    elif "export" in text:
        pygame.event.post(events.file_export)

    # If finishing up a previous command
    elif ("here" in text or "there" in text or "cheer" in text) and len(roomGrid.waitFunction) > 0:
        location = get_position(text)
        pygame.event.post(pygame.event.Event(events.ui_type, method="finish_waiting", location=location))

    # Creating things
    elif "add" in text or "create" in text:
        create(text)
    
    # Moving things
    # fruit is a keyword because Google thinks "fruit" and "cocktail" go together real nice...
    elif "move" in text or "relocate" in text or "fruit" in text:
        move(text)

    # Renaming things
    elif "rename" in text:
        rename(text)

    # Resizing things
    elif "resize" in text:
        resize(text)

    # Deleting things
    elif "remove" in text or "delete" in text:
        delete(text)
            
    pygame.event.post(events.done_listening_event)
    return True


# Listen for voice commands.
def listen(roomGrid):
    with open(SPEECH_CRED_FILE) as f:
        GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()

    context_list = list(COMMANDS.union(obj_types.possible))

    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=2)
            while True:
                if roomGrid.dead:
                    break

                audio = r.listen(source, phrase_time_limit=6)

                try:
                    pygame.event.post(events.capture_space_event)
                    text = r.recognize_google_cloud(audio, 
                                                    language="en-us",
                                                    credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS,
                                                    preferred_phrases=context_list)
                    try:
                        res = process_command(text, roomGrid)
                    except:
                        print("There was an error processing and executing the command.")
                        pygame.event.post(events.error_listening_event)
                    if not res:
                        break
                except sr.UnknownValueError:
                    pygame.event.post(events.error_listening_event)
                except:
                    print("Could not request results from Google Cloud Speech service.")
                    pygame.event.post(pygame.event.Event(events.error_type, error = "Speech recognition error."))
    except OSError:
        pygame.event.post(pygame.event.Event(events.error_type, error = "Could not connect to a microphone."))
