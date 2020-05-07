import pygame
import speech_recognition as sr
from time import sleep

import events

SPEECH_CRED_FILE = "../../Dropbox/College/2019-2020/6.835/Project/6835-95e43858e35a.json"

def correct_text(text):
    """Because Google gives English, not commands"""

    text = text.lower()
    text = text.replace("-", " ")
    text = text.split(" ")

    conversions = [
        [["one", "won"], "1"],
        [["to", "too", "two"], "2"],
        [["three", "free"], "3"],
        [["four"], "4"],
        [["five"], "5"],
        [["six"], "6"],
        [["seven"], "7"],
        [["eight", "ate", "hate"], "8"],
        [["nine"], "9"],
        [["ten"], "10"],
        [["+"], "and"],
        [["x"], "by"],
        [["buy"], "by"],
        [["criticize", "play"], "create a size"]
    ]

    for i in range(len(text)):
        for conversion in conversions:
            if text[i] in conversion[0]:
                text[i] = conversion[1]
                
    return text

def either_side(text, delimiter = "and", default = [-1, -1]):
    """Take form 12 AND 15 to return [12, 15] for example"""
    if delimiter in text:
        pos = text.index(delimiter)
        if text[pos - 1].isnumeric() and text[pos + 1].isnumeric():
            return [int(text[pos - 1]), int(text[pos + 1])]
        else:
            return default
    else:
        return default

def process_command(text, roomGrid):
    """Process voice commands. Returns False if program should quit."""

    text = correct_text(text)
    print(text)

    # Program controls
    if "quit" in text or "bye" in text or "exit" in text or "close" in text or "goodbye" in text:
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        return False
    elif "open" in text:
        pygame.event.post(events.file_open)
    elif "new" in text and ("design" in text or "room" in text or "file" in text):
        pygame.event.post(events.file_new)
    elif "save" in text:
        pygame.event.post(events.file_save)

    # If finishing up a previous command
    elif ("here" in text or "there" in text or "cheer" in text) and len(roomGrid.waitFunction) > 0:
        pygame.event.post(pygame.event.Event(events.ui_type, method="finish_waiting"))

    # Creating things
    elif "add" in text or "create" in text:
        location = [-1, -1]
        size = [1, 1]
        outline = 0
        obj_type = "cocktail"
        
        # Parameters
        if "at" in text:
            location = either_side(text, "and")
            location[0] -= 1
            location[1] -= 1
        if "by" in text or "size" in text:
            size = either_side(text, "by", [1, 1])
        if "called" in text:
            called = text[text.index("called") + 1:]
            called = " ".join(called)
        else:
            called = None

        # Object types
        if "cocktail" in text or "round" in text:
            shape = "circle"
            color = (70, 70, 70)
            obj_type = "cocktail"
            text_color = (255, 255, 255)
        elif "table" in text or "rectangle" in text:
            shape = "rectangle"
            color = (95, 32, 0)
            obj_type = "table"
            text_color = (255, 255, 255)
        elif "room" in text or "salon" in text:
            shape = "rectangle"
            color = (255, 0, 0)
            outline = 2
            obj_type = "room"
            text_color = (0, 0, 0)
        elif "couch" in text or "sofa" in text:
            shape = "rectangle"
            color = (154, 0, 130)
            obj_type = "couch"
            text_color = (255, 255, 255)
        else:
            shape = None
        
        if shape is not None:
            # Post event
            pygame.event.post(
                pygame.event.Event(events.design_type,
                                method="create",
                                shape=shape,
                                location=location,
                                color=color,
                                size=size,
                                outline=outline,
                                obj_type=obj_type,
                                text=called,
                                text_color=text_color))
    
    # Moving things
    # fruit is a keyword because Google thinks "fruit" and "cocktail" go together real nice...
    elif "move" in text or "relocate" in text or "fruit" in text:
        location = [-1, -1]
        to_location = [-1, -1]

        # Parameters (if location given in speech command)
        if "at" in text:
            location = either_side(text, "and")
            location[0] -= 1
            location[1] -= 1
            remaining_text = text[(text.index("and") + 1):]
        else:
            remaining_text = text

        if "and" in remaining_text:
            to_location = either_side(remaining_text, "and")
            to_location[0] -= 1
            to_location[1] -= 1

        # Object types
        if "cocktail" in text:
            obj_type = "cocktail"
        elif "table" in text:
            obj_type = "table"
        elif "room" in text:
            obj_type = "room"
        elif "couch" in text or "sofa" in text:
            obj_type = "couch"
        elif "this" in text or "that" in text:
            obj_type = "any"

        # Post event
        evt = pygame.event.Event(events.design_type, method="move", location=location, to_location=to_location, obj_type=obj_type)
        pygame.event.post(evt)

    # Renaming things
    elif "rename" in text:
        location = [-1, -1]

        # Parameters
        if "at" in text:
            location = either_side(text, "and")
            location[0] -= 1
            location[1] -= 1

        if "to" in text:
            called = text[text.index("to") + 1:]
            called = " ".join(called)
        elif "as" in text:
            called = text[text.index("as") + 1:]
            called = " ".join(called)
        elif "2" in text:
            called = text[text.index("2") + 1:]
            called = " ".join(called)
        else:
            called = None

        # Object types
        if "cocktail" in text:
            obj_type = "cocktail"
        elif "table" in text:
            obj_type = "table"
        elif "room" in text:
            obj_type = "room"
        elif "couch" in text or "sofa" in text:
            obj_type = "couch"
        elif "this" in text or "that" in text:
            obj_type = "any"

        # Post event
        evt = pygame.event.Event(events.design_type, method="rename", location=location, obj_type=obj_type, text=called)
        pygame.event.post(evt)

    # Deleting things
    elif "remove" in text or "delete" in text:
        location = [-1, -1]

        # Parameters
        if "at" in text:
            location = either_side(text, "and")
            location[0] -= 1
            location[1] -= 1

        # Object types
        if "cocktail" in text:
            obj_type = "cocktail"
        elif "table" in text:
            obj_type = "table"
        elif "room" in text:
            obj_type = "room"
        elif "couch" in text or "sofa" in text:
            obj_type = "couch"
        elif "this" in text or "that" in text:
            obj_type = "any"

        # Post event
        evt = pygame.event.Event(events.design_type, method="delete", location=location, obj_type=obj_type)
        pygame.event.post(evt)
            
    pygame.event.post(events.done_listening_event)
    return True

def listen(roomGrid):
    with open(SPEECH_CRED_FILE) as f:
        GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()

    r = sr.Recognizer()
    r.energy_threshold = 1000
    with sr.Microphone() as source:
        while True:
            if roomGrid.dead:
                break

            audio = r.listen(source, phrase_time_limit=6)

            try:
                pygame.event.post(events.capture_space_event)
                text = r.recognize_google_cloud(audio, 
                                                language="en-us",
                                                credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS,
                                                preferred_phrases=["create", "save", "add", "insert", "delete", "remove", "goodbye", "exit", "quit", "new", "open", "move", "relocate", "here", "there"])
                try:
                    res = process_command(text, roomGrid)
                except:
                    print("your code is wrong")
                if not res:
                    break
            except sr.UnknownValueError:
                print("Google Cloud Speech could not understand audio")
                pygame.event.post(events.done_listening_event)
            except:
                print("Could not request results from Google Cloud Speech service")
                pygame.event.post(pygame.event.Event(events.error_type, error = "Speech recognition error."))
