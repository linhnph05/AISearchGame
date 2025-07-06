import pygame, sys
import os, number

DARK_BG = (16, 24, 40)        
CARD_BG = (239, 68, 68)       
ACCENT_RED = (249, 120, 102)  
ACCENT_ORANGE = (250, 139, 72) 
WHITE = (255, 255, 255)
LIGHT_GRAY = (212, 213, 216)
TRANSPARENT = (0, 0, 0, 0)

pygame.init()

FPS = 60
fpsClock = pygame.time.Clock()

screen = pygame.display.set_mode((number.WINDOWWIDTH, number.WINDOWHEIGHT))
pygame.display.set_caption('Rush Hour Solver')

icon = pygame.image.load("Resource/icon.png")
pygame.display.set_icon(icon)

fontHeading = pygame.font.SysFont('Arial', 70, bold=True)
fontSubheading = pygame.font.SysFont('Arial', 30, bold=True)
fontInline = pygame.font.SysFont('Arial', 28, bold=True)

def drawRoundedRect(surface, color, rect, radius=15):
    rect = pygame.Rect(rect)
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    return rect

def renderGradientText(text, font, color1, color2):
    textSolid = font.render(text, True, (255, 255, 255))
    textRect = textSolid.get_rect()
    w, h = textRect.size

    gradSurf = pygame.Surface((w, h), pygame.SRCALPHA)
    for x in range(w):
        t = x / (w - 1)
        r = int(color1[0] + t * (color2[0] - color1[0]))
        g = int(color1[1] + t * (color2[1] - color1[1]))
        b = int(color1[2] + t * (color2[2] - color1[2]))
        pygame.draw.line(gradSurf, (r, g, b), (x, 0), (x, h))

    gradSurf.blit(textSolid, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return gradSurf

class Button:
    def __init__(self, x, y, width, height, text, font, radius=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.radius = radius
        self.isHovered = False
        
    def draw(self, surface, mousePosition):
        self.isHovered = self.rect.collidepoint(mousePosition)
        
        if self.isHovered:
            bgColor = (247, 9, 9)
        else:
            bgColor = CARD_BG
        
        drawRoundedRect(surface, bgColor, self.rect, self.radius)
        
        textSurface = self.font.render(self.text, True, WHITE)
        textRect = textSurface.get_rect(center=self.rect.center)
        surface.blit(textSurface, textRect)
    
    def handleClick(self, click):
        if self.isHovered and click:
            return True
        return False

playButton = Button(
    number.WINDOWWIDTH//2 - 175, number.WINDOWHEIGHT//2 + 40, 
    350, 60, "Play Game", fontInline
)

# optionsButton = Button(
#     number.WINDOWWIDTH//2 - 175, number.WINDOWHEIGHT//2 + 120, 
#     350, 60, "Options", fontInline
# )

exitButton = Button(
    number.WINDOWWIDTH//2 - 175, number.WINDOWHEIGHT//2 + 120, 
    350, 60, "Exit", fontInline
)

playIcon = pygame.image.load('Resource/playIcon2.jpg')
playIcon = pygame.transform.scale(playIcon, (60, 60))
settingIcon = pygame.image.load('Resource/setting.png')
settingIcon = pygame.transform.scale(settingIcon, (50, 50))
exitIcon = pygame.image.load('Resource/exit2.png')
exitIcon = pygame.transform.scale(exitIcon, (50, 50))

background = pygame.image.load("Resource/background2.jpg")
background = pygame.transform.scale(background, (number.WINDOWWIDTH, number.WINDOWHEIGHT))

def mainmenux():
    click = False
    mousePosition = pygame.mouse.get_pos()
    
    screen.blit(background, (0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            click = True
            try:
                number.Sound.clickChannel.play(number.Sound.clickSound)
            except (AttributeError, TypeError):
                pass
    

    titleText = renderGradientText("Rush Hour Solver", fontHeading, ACCENT_RED, ACCENT_ORANGE)
    screen.blit(titleText, (500, 60))
    
    subtitle = fontSubheading.render("AI-powered traffic puzzle solver", True, LIGHT_GRAY)
    screen.blit(subtitle, (550, 150))
    
    playButton.draw(screen, mousePosition)
    if playButton.handleClick(click):
        number.currentScreen = 1

    
    exitButton.draw(screen, mousePosition)
    if exitButton.handleClick(click):
        pygame.quit()
        sys.exit()
        
    screen.blit(playIcon, (600, 538))
    screen.blit(exitIcon, (620, 625))
    pygame.display.update()
    fpsClock.tick(FPS)