import pygame
from typing import List
from colors import Colors

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 font: pygame.font.Font, action=None, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action = action
        self.isHovered = False
        self.isPressed = False
        self.icon = icon
        self.enabled = True
        self.radius = 8  # Rounded corners
        
    def handleEvent(self, event):
        if not self.enabled:
            return
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.isPressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos) and self.isPressed:
                if self.action:
                    self.action()
            self.isPressed = False
        elif event.type == pygame.MOUSEMOTION:
            self.isHovered = self.rect.collidepoint(event.pos)
    
    def draw(self, screen):
        if not self.enabled:
            color = Colors.BUTTON_DISABLED
        elif self.isPressed:
            color = Colors.BUTTON_PRESSED
        elif self.isHovered:
            color = Colors.BUTTON_HOVER
        else:
            color = Colors.BUTTON_NORMAL
        
        # Draw rounded rectangle
        pygame.draw.rect(screen, color, self.rect, border_radius=self.radius)
        
        # Draw icon if available
        if self.icon:
            iconRect = self.icon.get_rect(centery=self.rect.centery)
            iconRect.left = self.rect.left + 10
            screen.blit(self.icon, iconRect)
            
        # Draw text
        textSurface = self.font.render(self.text, True, Colors.TEXT_COLOR)
        textRect = textSurface.get_rect(center=self.rect.center)
        screen.blit(textSurface, textRect)

class Dropdown:
    def __init__(self, x: int, y: int, width: int, height: int, options: List[str], 
                 font: pygame.font.Font, initialSelection: int = 0, label: str = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.font = font
        self.selectedIndex = initialSelection
        self.isOpen = False
        self.optionRects = []
        self.label = label
        self.radius = 8  # Rounded corners
        
        # Position option rects
        for i in range(len(options)):
            optionRect = pygame.Rect(x, y + height * (i + 1), width, height)
            self.optionRects.append(optionRect)
    
    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.isOpen = not self.isOpen
            elif self.isOpen:
                for i, optionRect in enumerate(self.optionRects):
                    if optionRect.collidepoint(event.pos):
                        self.selectedIndex = i
                        self.isOpen = False
                        break
                else:
                    self.isOpen = False
    
    def draw(self, screen):
        # Draw label if provided
        if self.label:
            labelSurface = self.font.render(self.label, True, Colors.TEXT_COLOR)
            labelY = self.rect.top - self.font.get_height() - 5
            screen.blit(labelSurface, (self.rect.left, labelY))
        
        # Draw main dropdown button with rounded corners and white background
        pygame.draw.rect(screen, Colors.WHITE, self.rect, border_radius=self.radius)
        
        # Draw text in black
        text = self.options[self.selectedIndex]
        textSurface = self.font.render(text, True, Colors.BLACK)
        textRect = textSurface.get_rect(centery=self.rect.centery)
        textRect.left = self.rect.left + 15
        screen.blit(textSurface, textRect)
        
        # Draw dropdown arrow (down arrow)
        arrowPoints = [
            (self.rect.right - 24, self.rect.centery - 3),  # Left point
            (self.rect.right - 16, self.rect.centery - 3),  # Right point
            (self.rect.right - 20, self.rect.centery + 3)   # Bottom point (tip)
        ]
        pygame.draw.polygon(screen, Colors.BLACK, arrowPoints)
        
        # Draw options if open
        if self.isOpen:
            # Draw dropdown box shadow
            shadowRect = pygame.Rect(
                self.rect.x, self.rect.y + self.rect.height,
                self.rect.width, len(self.options) * self.rect.height
            )
            pygame.draw.rect(screen, Colors.BLACK, shadowRect.inflate(6, 6), 
                            border_radius=self.radius)
            
            # Draw option items with white background and black text
            for i, (option, optionRect) in enumerate(zip(self.options, self.optionRects)):
                bgColor = Colors.WHITE
                if i == self.selectedIndex:
                    bgColor = Colors.LIGHT_GRAY  # Slightly gray for selected item
                
                pygame.draw.rect(screen, bgColor, optionRect, border_radius=self.radius)
                
                optionText = self.font.render(option, True, Colors.BLACK)
                optionTextRect = optionText.get_rect(centery=optionRect.centery)
                optionTextRect.left = optionRect.left + 15
                screen.blit(optionText, optionTextRect)
