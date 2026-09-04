import pygame
from src.state_machine import State
from src.ui_helpers import get_font, FancyButton, draw_gradient_bg, draw_text_centered, draw_onam_border
from config import *

class IntroState(State):
    def enter(self):
        self.btn_next = FancyButton("I'm Ready!", SCREEN_W // 2, SCREEN_H - 100)

    def exit(self):
        pass

    def handle_event(self, event):
        if self.btn_next.handle_event(event):
            self.machine.change_state("menu")

    def update(self, dt):
        pass

    def draw(self, surface):
        draw_gradient_bg(surface, ONAM_DEEP, ONAM_BROWN)
        draw_onam_border(surface)
        
        title = get_font(FONT_LG).render("The Legend of Maveli", True, GOLD)
        surface.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 80))
        
        story = [
            "According to the legend of Onam, the beloved",
            "King Maveli was pushed down into the underworld",
            "of Pathalam by Vamana.",
            "",
            "Once a year, he is allowed to return to Kerala",
            "to visit his people.",
            "",
            "But the path is long and difficult.",
            "He needs YOUR help to complete the traditions.",
            "WARNING: You only have 5 chances in total to succeed!"
        ]
        
        y = 180
        for line in story:
            draw_text_centered(surface, line, y, FONT_MD, ONAM_CREAM)
            y += 35
            
        self.btn_next.draw(surface)
