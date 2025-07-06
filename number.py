import pygame, sys
from pygame import mixer

pygame.init()
mixer.init()

currentScreen = 0

WINDOWWIDTH = 1500 
WINDOWHEIGHT = 1000 

class Sound():
    mainSound = mixer.Sound("Resource/music.mp3")
    mainChannel = mixer.find_channel()
    clickSound = mixer.Sound("Resource/click.mp3")
    clickChannel = mixer.find_channel()
    soundMaster = 100
    soundMusic = 10
    soundEffects = 100
    soundVoice = 100
