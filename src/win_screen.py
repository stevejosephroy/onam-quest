# ── Win Screen — Victory Celebration ─────────────────────────────────────────
import pygame, random, math
from src.state_machine import State
from src.ui_helpers import (
    get_font, FancyButton, TypewriterText, draw_pookalam_deco,
)
from src.effects import ParticleSystem, PetalParticle
from config import *


class WinState(State):
    """Full-color celebration — Mahabali has returned to Kerala!"""

    def enter(self):
        self.elapsed = 0.0
        self.phase = 0    # 0=silence, 1=shockwave, 2=celebration
        self.ring_r = 0.0
        self.main_text = None
        self.subtitle_vis = False
        self.particles = ParticleSystem()
        self.fw_timer = 0.0
        self.bloom_r = 0.0
        self.pulse = 0.0
        
        from src.asset_loader import get_spritesheet
        try:
            self.maveli_img = get_spritesheet("maveli_run.jpg", 2, 2)[0]
            self.maveli_img = pygame.transform.scale(self.maveli_img, (120, 120))
        except:
            self.maveli_img = None
            
        self.menu_btn = FancyButton("Main Menu", SCREEN_W // 2, SCREEN_H - 70,
                                    fill=(80, 40, 10), border=GOLD)
        self.menu_btn.enabled = False

    def exit(self):
        self.particles.clear()

    def handle_event(self, event):
        if self.menu_btn.enabled and self.menu_btn.handle_event(event):
            self.machine.change_state("menu")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if self.elapsed > 5.0:
                self.machine.change_state("menu")

    def update(self, dt):
        self.elapsed += dt
        self.particles.update(dt)
        if self.phase == 0 and self.elapsed >= 1.0: self.phase = 1
        if self.phase == 1 and self.elapsed >= 2.0: self.phase = 2
        if self.phase == 1:
            self.ring_r += 600 * dt
        if self.phase == 2:
            if not self.main_text:
                self.main_text = TypewriterText(
                    "Mahabali has returned to Kerala!", 100,
                    SCREEN_H // 2 - 60, FONT_XL, GOLD, 0.04, bold=True)
            self.main_text.update(dt)
            if self.main_text.done and not self.subtitle_vis:
                self.subtitle_vis = True
            if self.bloom_r < 180: self.bloom_r += 80 * dt
            self.fw_timer += dt
            if self.fw_timer > 0.35:
                self.fw_timer = 0
                self.particles.emit_firework(
                    random.randint(100, SCREEN_W - 100),
                    random.randint(60, SCREEN_H // 2),
                    count=25, color=random.choice([GOLD, ORANGE, PETAL_PINK,
                                                    PETAL_RED, KERALA_GREEN]))
            self.particles.emit_confetti(2)
            self.pulse += dt
            if self.elapsed > 5.0: self.menu_btn.enabled = True

    def draw(self, surface):
        if self.phase == 0:
            surface.fill(BLACK); return
        if self.phase == 1:
            surface.fill(BLACK)
            r = int(self.ring_r)
            if r > 2:
                s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                a = max(30, 255 - int(self.ring_r * 0.4))
                pygame.draw.circle(s, (*GOLD, a), (SCREEN_W // 2, SCREEN_H // 2),
                                   r, max(3, 8 - r // 100))
                surface.blit(s, (0, 0))
            return

        # Phase 2: warm gradient
        for y in range(SCREEN_H):
            ratio = y / SCREEN_H
            mid = abs(ratio - 0.45) * 2
            b = max(0.15, 1.0 - mid)
            surface.fill((int(50 + 120 * b), int(25 + 70 * b), int(5 + 15 * b)),
                         (0, y, SCREEN_W, 1))

        # Draw House (Traditional Kerala Tharavadu)
        hx, hy = SCREEN_W // 2, SCREEN_H // 2 + 30
        # Walls
        pygame.draw.rect(surface, (230, 220, 200), (hx - 120, hy - 60, 240, 80))
        # Pillars
        for i in range(4):
            pygame.draw.rect(surface, (80, 40, 20), (hx - 110 + i * 70, hy - 60, 10, 80))
        # Roof (Slanted)
        pts = [(hx - 150, hy - 60), (hx, hy - 130), (hx + 150, hy - 60)]
        pygame.draw.polygon(surface, (139, 69, 19), pts)
        pygame.draw.polygon(surface, (100, 50, 10), pts, 5)
        # Door
        pygame.draw.rect(surface, (60, 30, 10), (hx - 20, hy - 20, 40, 40))

        # Pookalam bloom
        if self.bloom_r > 10:
            draw_pookalam_deco(surface, SCREEN_W // 2, SCREEN_H // 2 + 70,
                               int(self.bloom_r), 90)
                               
        # Happy Maveli
        if self.maveli_img and self.bloom_r > 40:
            # Add a slight bounce
            bounce = math.sin(self.elapsed * 5) * 5
            m_rect = self.maveli_img.get_rect(center=(hx + 80, hy + 20 + bounce))
            surface.blit(self.maveli_img, m_rect)

        self.particles.draw(surface)

        if self.main_text:
            # Shadow
            if self.main_text.char_index > 0:
                f = get_font(FONT_XL, bold=True)
                sh = f.render(self.main_text.full_text[:self.main_text.char_index],
                              True, (40, 20, 0))
                surface.blit(sh, (102, SCREEN_H // 2 - 58))
            self.main_text.draw(surface)

        if self.subtitle_vis:
            f = get_font(FONT_TITLE, bold=True)
            p = 0.5 + 0.5 * math.sin(self.pulse * 3)
            txt = f.render("GAME COMPLETE", True,
                           (int(255 * (0.8 + 0.2 * p)), int(215 * (0.8 + 0.2 * p)), 0))
            r = txt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 30))
            glow = pygame.Surface((r.width + 40, r.height + 20), pygame.SRCALPHA)
            glow.fill((*GOLD, int(40 * p)))
            surface.blit(glow, (r.x - 20, r.y - 10))
            surface.blit(txt, r)

        if self.menu_btn.enabled:
            self.menu_btn.draw(surface)
