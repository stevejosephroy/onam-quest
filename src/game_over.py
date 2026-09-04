import pygame
from src.state_machine import State
from src.ui_helpers import get_font, FancyButton, draw_gradient_bg, draw_text_centered, draw_text_shadow
from config import SCREEN_W, SCREEN_H, RED, WHITE, BLACK

class GameOverState(State):
    def enter(self):
        self.restart_btn = FancyButton("Restart Game", SCREEN_W // 2, SCREEN_H // 2 + 100, fill=(80, 20, 20), border=RED)
        from src.asset_loader import get_sound
        get_sound("miss.wav").play()

    def exit(self):
        pass

    def handle_event(self, event):
        if self.restart_btn.handle_event(event):
            # Reset game data
            self.machine.game_data["lives"] = 5
            self.machine.game_data["levels_cleared"] = set()
            self.machine.change_state("level1")

    def update(self, dt):
        pass

    def draw(self, surface):
        draw_gradient_bg(surface, (40, 10, 10), BLACK)
        
        draw_text_centered(surface, "GAME OVER", SCREEN_H // 2 - 80, 80, RED, bold=True)
        draw_text_centered(surface, "You couldn't help Maveli reach Kerala...", SCREEN_H // 2, 30, WHITE)
        
        self.restart_btn.draw(surface)
