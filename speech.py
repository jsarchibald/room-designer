import pygame
import speech_recognition as sr
from time import sleep

import events

def process_command(text):
    """Process voice commands. Returns False if program should quit."""

    text = text.lower()
    print(text)

    if "quit" in text or "bye" in text:
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        return False

    if "add" in text or "create" in text:
        location = [-1, -1]
        if "at" in text:
            # TODO
            location = [-1, -1]
        if "cocktail" in text or "round" in text:
            shape = "circle"
            color = (0, 255, 0)
        else:
            # TODO
            shape = "circle"
            color = (0, 0, 255)
        
        pygame.event.post(pygame.event.Event(events.create_type, shape=shape, location=location, color=color))
            
    pygame.event.post(events.done_listening_event)
    return True

def listen():
    with open("../../Dropbox/College/2019-2020/6.835/Project/6835-95e43858e35a.json") as f:
        GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()

    r = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            print("Say something!")
            audio = r.listen(source)

            print("let's see...")

            try:
                pygame.event.post(events.capture_space_event)
                text = r.recognize_google_cloud(audio, language="en-us", credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
                res = process_command(text)
                if not res:
                    break
            except sr.UnknownValueError:
                print("Google Cloud Speech could not understand audio")
                pygame.event.post(events.done_listening_event)
            except:
                print("Could not request results from Google Cloud Speech service")
                pygame.event.post(pygame.event.Event(events.error_type, error = "Speech recognition error."))