# ── Menu State — Festival Level Select ───────────────────────────────────────
import pygame
import math
import random
from src.state_machine import State
from src.ui_helpers import (
    get_font, FancyButton, draw_gradient_bg, draw_pookalam_deco,
    draw_text_centered, draw_text_shadow, draw_onam_border,
    draw_nilavilakku,
)
from src.effects import PetalParticle, ParticleSystem
from config import *

_LEVELS = [
    ("\U0001f338  Pookalam",        "level1", set(),           PETAL_PINK, 
     ["Drag and drop the beautiful floral layers", "in STRICT order from largest to smallest", "to create a stunning Pookalam!", "If you make a mistake, you fail!"]),
    ("\U0001f35b  Sadya",           "level2", {1},             ONAM_GOLD, 
     ["Serve the grand Sadya feast!", "Drag each dish to its correct spot", "on the banana leaf."]),
    ("\U0001f6a3  Vallam Kali",     "level3", {1, 2},          WATER_LIGHT, 
     ["Race the snake boat (Chundan Vallam)!", "Press LEFT/RIGHT arrows (or tap the", "Left/Right sides of the screen)", "to steer around the rocks."]),
    ("\U0001f483  Thiruvathira",    "level4", {1, 2, 3},       LAMP_FLAME, 
     ["Perform the traditional Thiruvathira dance!", "Watch the rhythm and press SPACEBAR", "(or tap anywhere on screen) exactly", "when the beat reaches the center."]),
    ("\U0001f525  Escape Pathalam", "level5", {1, 2, 3, 4},    PATH_FIRE_RED, 
     ["The Final Challenge! Maveli is escaping Pathalam.", "Press UP (or tap the Top Half of screen) to Jump.", "Press DOWN (or hold Bottom Half) to Duck."]),
]


class MenuState(State):
    """Beautiful Onam-themed level select with decorative elements."""

    def enter(self):
        self.cleared = self.machine.game_data["levels_cleared"]
        self.particles = ParticleSystem()
        self.elapsed = 0.0
        self._build_buttons()

    def _build_buttons(self):
        self.buttons: list[tuple[FancyButton, int, str, list[str]]] = []
        
        # Only show the exact next challenge (len(cleared) + 1)
        target_num = len(self.cleared) + 1

        for i, (label, state_name, required, accent, desc) in enumerate(_LEVELS):
            num = i + 1
            if num != target_num:
                continue

            btn = FancyButton(
                label, SCREEN_W // 2, 320,  # Centered Y
                w=320, h=55,
                fill=(50, 25, 8) if num < 5 else (30, 5, 5),
                border=accent,
                text_color=ONAM_CREAM,
                hover_fill=ONAM_BROWN if num < 5 else (60, 15, 15),
            )
            self.buttons.append((btn, num, state_name, desc))

    def exit(self):
        self.particles.clear()

    def handle_event(self, event):
        self.cleared = self.machine.game_data["levels_cleared"]
        for btn, num, state_name, desc in self.buttons:
            if btn.handle_event(event):
                self.machine.game_data["next_level_id"] = state_name
                self.machine.game_data["next_level_desc"] = desc
                self.machine.game_data["next_level_title"] = btn.text
                self.machine.change_state("instruction")
                return
        if event.type == pygame.KEYDOWN:
            for btn, num, state_name, desc in self.buttons:
                if event.unicode == str(num):
                    self.machine.game_data["next_level_id"] = state_name
                    self.machine.game_data["next_level_desc"] = desc
                    self.machine.game_data["next_level_title"] = btn.text
                    self.machine.change_state("instruction")
                    return

    def update(self, dt):
        self.elapsed += dt
        self.cleared = self.machine.game_data["levels_cleared"]
        self._build_buttons()
        self.particles.update(dt)
        if random.random() < 0.08:
            self.particles.add(PetalParticle(
                random.randint(50, SCREEN_W - 50), -10))

    def _draw_progress_bar(self, surface):
        cleared_count = min(5, len(self.cleared))
        bar_w = 400
        bar_x = SCREEN_W // 2 - bar_w // 2
        bar_y = 150  # Shifted down slightly
        
        # Draw line
        pygame.draw.line(surface, GRAY, (bar_x, bar_y), (bar_x + bar_w, bar_y), 4)
        
        # Draw progress line
        if cleared_count > 0:
            progress_w = int((cleared_count / 4.0) * bar_w) if cleared_count < 5 else bar_w
            pygame.draw.line(surface, ONAM_GOLD, (bar_x, bar_y), (bar_x + progress_w, bar_y), 4)
            
        # Draw nodes
        for i in range(5):
            nx = bar_x + int((i / 4.0) * bar_w)
            color = ONAM_GOLD if i <= cleared_count else GRAY
            pygame.draw.circle(surface, color, (nx, bar_y), 10)
            if i == 4:
                pygame.draw.circle(surface, PATH_FIRE_RED, (nx, bar_y), 6) # Pathalam target
                
        # Draw Maveli marker at current progress
        mx = bar_x + int((cleared_count / 4.0) * bar_w)
        pygame.draw.circle(surface, (255, 200, 150), (mx, bar_y - 20), 12) # Maveli head
        pygame.draw.polygon(surface, GOLD, [(mx - 10, bar_y - 28), (mx, bar_y - 40), (mx + 10, bar_y - 28)]) # Crown
        f = get_font(FONT_SM - 4)
        lbl = f.render("Maveli's Journey", True, ONAM_CREAM)
        surface.blit(lbl, (SCREEN_W // 2 - lbl.get_width() // 2, bar_y - 65))

    def draw(self, surface: pygame.Surface):
        draw_gradient_bg(surface, ONAM_DEEP, ONAM_BROWN)

        # Lamps on sides
        draw_nilavilakku(surface, 80, SCREEN_H - 40, 90)
        draw_nilavilakku(surface, SCREEN_W - 80, SCREEN_H - 40, 90)

        # Title
        draw_text_shadow(surface, "Onam Festival",
                         SCREEN_W // 2 - 155, 40, FONT_XL, GOLD, offset=2)
                         
        self._draw_progress_bar(surface)

        # Buttons
        for btn, num, state_name, desc in self.buttons:
            btn.draw(surface)

        # Pulsing hint
        cleared_count = sum(1 for x in self.cleared if x <= 4)
        if cleared_count == 4 and 5 not in self.cleared:
            pulse = 0.5 + 0.5 * math.sin(self.elapsed * 3)
            draw_text_centered(surface,
                               "\u26a0  Pathalam gate is open... save Mahabali!",
                               SCREEN_H - 50, FONT_SM,
                               (255, int(100 * pulse), int(50 * pulse)))

        self.particles.draw(surface)
        draw_onam_border(surface)
