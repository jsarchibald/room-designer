# Room Designer
A multimodal interface for basic interior design.

## Setting up the program
To run this on your machine, follow these steps!

1. Install Python 3. I wrote and tested this code in Python 3.7.2.
2. Clone the repository.
3. Use the command prompt/terminal to navigate to the repository's directory. Install the required libraries by running `pip install -r requirements.txt`.
- I recommend setting up a virtual environment before doing this, as by running `virtualenv env` followed by `env\scripts\activate`.
4. Get a Google Cloud Speech-to-Text API key [here](https://cloud.google.com/speech-to-text). You will likely have to create a new project. You should be able to download a `JSON` file with credentials to your computer.
5. Copy the file path to your Google credentials. Open `settings.py` and set `SPEECH_CRED_FILE` to that file path.
6. Make sure your computer microphone and Leap controller are connected.
7. In your terminal, run `python main.py` to open in full-screen, or `python main.py w` to open in windowed mode.

### Note on operating environment
I wrote and tested this code on a Windows 10 machine running Python 3.7.2. I cannot speak to whether, or how well, it works on other systems.

## Code organization
The directories containing code belong to libraries:

- `pyleap`: the Leap Motion Controller library.
- `speech_recognition`: would just use the [PyPI version](https://pypi.org/project/SpeechRecognition/), but that version has a one-character error on line 924 that makes it a disappointing impossibility. The error is corrected in the version included here.

My code is organized into the following files:
- `events.py`: definitions of Pygame user event types used throughout the codebase.
- `graphics.py`: the objects defining the grid, grid spaces, and room objects, and how to display them on screen.
- `handle_events.py`: all events relating to how the main program should respond to events pushed out from the voice command parser.
- `main.py`: the main Pygame loop and voice listener thread is handled here. Data from the Leap are also pulled from here.
- `settings.py`: global variables that are used across these files.
- `speech_helpers.py`: some helper functions to help process speech commands.
- `speech.py`: the listener thread that calls the Google Cloud Speech API, parses the text results into usable commands, and pushes relevant events to the Pygame event queue (to be handled in `main.py` and ultimately `handle_events.py`).

## Third-party graphics and fonts

- Font [Roboto](https://www.fontsquirrel.com/fonts/roboto), offered under the Apache v2.0 License.

## Third-party libraries

- FLAC, offered under the GNU GPL v2 License. (Packaged with Speech Recognition library.)

- [Pyleap](https://github.com/eranegozy/pyleap), offered under the GNU GPL v3 License.

- [Speech Recognition](https://github.com/Uberi/speech_recognition), offered under the BSD 3-Clause License.

All licenses of the libraries whose source code is redistributed in this repository are located in the respective directories of said library.
