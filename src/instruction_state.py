import pygame
from src.state_machine import State
from src.ui_helpers import get_font, FancyButton, draw_gradient_bg, draw_text_centered, draw_onam_border
from config import *

class InstructionState(State):
    def enter(self):
        # We expect game_data to have "next_level_id" and "next_level_desc"
        self.target_state = self.machine.game_data.get("next_level_id", "menu")
        self.desc = self.machine.game_data.get("next_level_desc", ["Help Maveli!"])
        self.title = self.machine.game_data.get("next_level_title", "Instructions")
        
        self.btn_play = FancyButton("Play Level", SCREEN_W // 2, SCREEN_H - 120)

    def exit(self):
        pass

    def handle_event(self, event):
        if self.btn_play.handle_event(event):
            self.machine.change_state(self.target_state)

    def update(self, dt):
        pass

    def draw(self, surface):
        draw_gradient_bg(surface, ONAM_DEEP, ONAM_BROWN)
        draw_onam_border(surface)
        
        # Title
        title_surf = get_font(FONT_LG).render(self.title, True, GOLD)
        surface.blit(title_surf, (SCREEN_W // 2 - title_surf.get_width() // 2, 100))
        
        # Instructions
        y = 220
        for line in self.desc:
            draw_text_centered(surface, line, y, FONT_MD, ONAM_CREAM)
            y += 40
            
        lives = self.machine.game_data.get("lives", 5)
        draw_text_centered(surface, f"WARNING: You only have {lives} chances left to help Maveli!", SCREEN_H - 180, FONT_SM, (255, 100, 100))
            
        self.btn_play.draw(surface)
