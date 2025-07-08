import pygame, number
from pygame.locals import *
from pygame import mixer
import mainMenu,  option
import game

WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)

pygame.init()
mixer.init()

FPS = 60
fpsClock = pygame.time.Clock()

screen = pygame.display.set_mode((number.WINDOWWIDTH, number.WINDOWHEIGHT))
pygame.display.set_caption('Rush Hour Solver')
background = pygame.image.load("Resource/background.jpg")
background = pygame.transform.scale(background, (number.WINDOWWIDTH, number.WINDOWHEIGHT))

icon = pygame.image.load("Resource/icon.png")
pygame.display.set_icon(icon)


number.Sound.mainSound.set_volume(number.Sound.soundMusic/float(100))
number.Sound.mainChannel.play(number.Sound.mainSound)
number.Sound.mainSound.play(loops=-1)

while True:
    if number.currentScreen == 0: mainMenu.mainmenux()
    if number.currentScreen == 1: game.main()
    if number.currentScreen == 2: option.main()
