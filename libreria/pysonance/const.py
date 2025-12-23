from enum import Enum


CHUNK = 1024
SRATE = 48000

class State(Enum):
    STOP = 0
    PLAY = 1
    PAUSE = 2