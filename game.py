import pygame, number
from pygame import mixer

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
