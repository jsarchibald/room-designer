import pygame
import speech_recognition as sr
from time import sleep

import events

def number_synonyms(text):
    """to and too and two are 2"""
    for i in range(len(text)):
        if text[i] in ["one", "won"]:
            text[i] = "1"
        if text[i] in ["to", "too", "two"]:
            text[i] = "2"
    return text

def either_side(text, delimiter = "and", default = [-1, -1]):
    """Take form 12 AND 15 to return [12, 15] for example"""
    if delimiter in text:
        pos = text.index(delimiter)
        text = number_synonyms(text)
        print(text)
        if text[pos - 1].isnumeric() and text[pos + 1].isnumeric():
            return [int(text[pos - 1]), int(text[pos + 1])]
        else:
            return default
    else:
        return default

def process_command(text):
    """Process voice commands. Returns False if program should quit."""

    text = text.lower()
    print(text)

    if "quit" in text or "bye" in text or "exit" in text or "close" in text:
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        return False

    text = text.replace("buy", "by")
    text = text.replace("criticize", "create a size")
    text = text.split(" ")
    print(text)
    if "add" in text or "create" in text:
        location = [-1, -1]
        size = [1, 1]
        if "at" in text:
            location = either_side(text, "and")
            location[0] -= 1
            location[1] -= 1
        if "by" in text or "size" in text:
            size = either_side(text, "by", [1, 1])
        if "cocktail" in text or "round" in text:
            shape = "circle"
            color = (0, 255, 0)
        elif "table" in text or "rectangle" in text:
            shape = "rectangle"
            color = (0, 0, 255)
        else:
            # TODO
            shape = "circle"
            color = (0, 0, 255)
        
        pygame.event.post(pygame.event.Event(events.create_type, shape=shape, location=location, color=color, size=size))
            
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
                try:
                    res = process_command(text)
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