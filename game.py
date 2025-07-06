import pygame, number
from enum import Enum
from typing import List, Tuple, Optional
import time
from pygame import mixer
from dataclasses import dataclass
import heapq
import tracemalloc

from vehicle import Vehicle, Board
from colors import Colors
from gameModels import GameState, Algorithm, Car
from ui import Button, Dropdown
from rushHourGame import RushHourGame

background = pygame.image.load("Resource/starBG.jpeg")
background = pygame.transform.scale(background, (number.WINDOWWIDTH, number.WINDOWHEIGHT))

pygame.init()
mixer.init()

def main():
    clock = pygame.time.Clock()
    game = RushHourGame()
    
    running = True
    while running and number.currentScreen == 1:
        
        running = game.runFrame()
        clock.tick(60)
