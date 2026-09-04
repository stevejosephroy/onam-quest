# ── Boot State — Festival Loading Screen ─────────────────────────────────────
import pygame
import math
import random
from src.state_machine import State
from src.ui_helpers import (
    get_font, draw_gradient_bg, draw_pookalam_deco, draw_text_centered,
    draw_text_shadow, draw_onam_border,
)
from src.effects import PetalParticle, ParticleSystem
from config import *


class BootState(State):
    """Beautiful Onam-themed loading screen with blooming pookalam."""

    def enter(self):
        self.elapsed = 0.0
        self.bloom_radius = 0.0
        self.bloom_target = 140.0
        self.progress = 0.0          # 0→1 loading bar
        self.phase = 0               # 0=loading, 1=ready
        self.particles = ParticleSystem()

        self.load_items = [
            "Loading traditions...",
            "Preparing pookalam petals...",
            "Setting up the sadya feast...",
            "Tuning the boat drums...",
            "Lighting the nilavilakku...",
            "Connecting to Mahabali...",
        ]
        self.current_item = 0
        self.item_timer = 0.0

    def exit(self):
        self.particles.clear()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.phase == 1:
                    self.machine.change_state("intro")
                else:
                    self.phase = 1
                    self.progress = 1.0
                    self.bloom_radius = self.bloom_target
        if event.type == pygame.MOUSEBUTTONDOWN and self.phase == 1:
            self.machine.change_state("intro")

    def update(self, dt):
        self.elapsed += dt
        self.particles.update(dt)

        if self.phase == 0:
            self.progress = min(1.0, self.progress + dt * 0.18)
            self.bloom_radius = min(self.bloom_target,
                                    self.bloom_radius + dt * 35)
            self.item_timer += dt
            if self.item_timer > 0.7 and self.current_item < len(self.load_items) - 1:
                self.item_timer = 0
                self.current_item += 1

            # Petals
            if random.random() < 0.15:
                self.particles.add(PetalParticle(
                    random.randint(100, SCREEN_W - 100), -10))

            if self.progress >= 1.0:
                self.phase = 1
        else:
            # Phase 1: ready — keep petals flowing
            if random.random() < 0.2:
                self.particles.add(PetalParticle(
                    random.randint(50, SCREEN_W - 50), -10))

    def draw(self, surface: pygame.Surface):
        draw_gradient_bg(surface, ONAM_DEEP, ONAM_BROWN)

        cx, cy = SCREEN_W // 2, 300

        # Pookalam bloom
        if self.bloom_radius > 10:
            draw_pookalam_deco(surface, cx, cy, int(self.bloom_radius), 150)

        # Title
        draw_text_shadow(surface, "Escape Pathalam",
                         cx - 220, 80, FONT_TITLE, GOLD, offset=3)
        draw_text_centered(surface, "An Onam Adventure", 155, FONT_LG,
                           ONAM_CREAM)

        # Loading bar
        bar_w, bar_h = 400, 18
        bar_x = cx - bar_w // 2
        bar_y = 480
        pygame.draw.rect(surface, ONAM_DEEP, (bar_x - 2, bar_y - 2,
                                               bar_w + 4, bar_h + 4),
                         border_radius=9)
        fill_w = int(bar_w * self.progress)
        if fill_w > 0:
            pygame.draw.rect(surface, GOLD,
                             (bar_x, bar_y, fill_w, bar_h),
                             border_radius=8)

        # Loading text
        if self.phase == 0:
            item = self.load_items[self.current_item]
            draw_text_centered(surface, item, bar_y + 30, FONT_SM,
                               ONAM_LIGHT)
        else:
            # Pulsing "Press ENTER"
            pulse = 0.5 + 0.5 * math.sin(self.elapsed * 4)
            alpha = int(180 + 75 * pulse)
            color = (255, 255, int(200 * pulse))
            draw_text_centered(surface, "Press ENTER to begin",
                               bar_y + 35, FONT_MD, color)

        # Subtitle
        draw_text_centered(surface,
                           "Help Mahabali escape Pathalam and return to Kerala",
                           SCREEN_H - 100, FONT_SM, ONAM_GOLD)

        # Particles
        self.particles.draw(surface)

        draw_onam_border(surface)
