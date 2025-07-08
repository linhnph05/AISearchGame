from enum import Enum

class GameState(Enum):
    STOPPED = 1
    PLAYING = 2
    PAUSED = 3
    FINISHED = 4

class Algorithm(Enum):
    BFS = "BFS"
    IDS = "IDS"
    UCS = "UCS"
    A_STAR = "A*"

