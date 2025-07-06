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

class Car:
    def __init__(self, x: int, y: int, size: int, orientation: str, carId: int = 0):
        self.x = x  # row position (from file format)
        self.y = y  # column position (from file format)
        self.size = size
        self.orientation = orientation  # 'H' for horizontal, 'V' for vertical
        self.carId = carId
        self.isTarget = carId == 0  # First car (car 0) is the target car (red car)
