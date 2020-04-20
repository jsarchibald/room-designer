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
            except sr.RequestError as e:
                print("Could not request results from Google Cloud Speech service; {0}".format(e))