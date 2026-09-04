# ── Level 1 — Pookalam (Concentric Ring Puzzle) ─────────────────────────────────
import pygame, random, math
from src.state_machine import State
from src.ui_helpers import (
    get_font, FancyButton, draw_gradient_bg, draw_text_centered,
    draw_text_shadow, draw_onam_border,
)
from src.asset_loader import get_image, get_sound
from config import *

# Define the rings: (r_inner, r_outer)
_RINGS = [
    (110, 150),
    (75, 110),
    (40, 75),
    (0, 40),
]

def extract_ring(surface, r_inner, r_outer):
    w, h = surface.get_size()
    cx, cy = w // 2, h // 2
    ring = pygame.Surface((w, h), pygame.SRCALPHA)
    ring.blit(surface, (0, 0))
    for x in range(w):
        for y in range(h):
            d = math.hypot(x - cx, y - cy)
            if d < r_inner or d > r_outer:
                ring.set_at((x, y), (0,0,0,0))
    return ring

class _PookalamPiece:
    def __init__(self, idx, img_surface, r_outer, target, start):
        self.idx = idx
        self.img = img_surface
        self.size = r_outer * 2
        self.click_radius = r_outer
        self.target = list(target)
        self.home = list(start)
        self.pos = list(start)
        self.placed = False
        self.dragging = False
        self.flash = 0.0
        self.shake = 0.0

    def draw(self, surface, as_target=False):
        x, y = int(self.pos[0]), int(self.pos[1])
        if self.shake > 0:
            x += random.randint(-5, 5)
            y += random.randint(-5, 5)

        if as_target:
            # Dim dashed-feel outline
            s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(s, (200, 180, 150, 60), (self.size // 2, self.size // 2),
                               self.size // 2, 3)
            surface.blit(s, (self.target[0] - self.size // 2,
                             self.target[1] - self.size // 2))
            return

        # Draw image (img is 300x300, we must center it correctly!)
        rect = self.img.get_rect(center=(x, y))
        surface.blit(self.img, rect)
        
        # Highlight outline
        if self.flash > 0:
            pygame.draw.circle(surface, WHITE, (x, y), self.size // 2, 4)
        elif self.placed:
            pygame.draw.circle(surface, GOLD, (x, y), self.size // 2 + 2, 2)


class Level1Pookalam(State):
    def enter(self):
        cx, cy = SCREEN_W // 3 + 20, SCREEN_H // 2 + 20
        self.target_center = (cx, cy)
        
        # Load the single full image
        full_img = get_image("pookalam_base.jpg", scale=(300, 300))
        
        self.pieces: list[_PookalamPiece] = []
        n = len(_RINGS)
        order = list(range(n))
        random.shuffle(order)
        for i in range(n):
            r_inner, r_outer = _RINGS[i]
            ring_img = extract_ring(full_img, r_inner, r_outer)
            sx = SCREEN_W - 140
            sy = 100 + order[i] * 120
            self.pieces.append(_PookalamPiece(i, ring_img, r_outer, (cx, cy), (sx, sy)))
            
        self.expected_idx = 0
        self.dragged = None
        self.complete = False
        self.failed = False
        self.complete_timer = 0.0
        self.continue_btn = FancyButton("Continue", SCREEN_W // 2,
                                        SCREEN_H // 2 + 80)
        self.retry_btn = FancyButton("Retry", SCREEN_W // 2, SCREEN_H // 2 + 80,
                                     fill=(10, 30, 80), border=RED)

    def exit(self): pass

    def handle_event(self, event):
        if self.complete:
            if self.complete_timer > 1.0 and self.continue_btn.handle_event(event):
                self.machine.game_data["levels_cleared"].add(1)
                self.machine.change_state("menu")
            return
        if self.failed:
            if self.retry_btn.handle_event(event):
                self.machine.game_data["lives"] -= 1
                if self.machine.game_data["lives"] <= 0:
                    self.machine.change_state("game_over")
                else:
                    self.machine.change_state("level1")
            return
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Check smallest pieces first for easier selection
            for p in reversed(self.pieces):
                if p.placed: continue
                d = math.hypot(mx - p.pos[0], my - p.pos[1])
                if d < p.click_radius:
                    p.dragging = True
                    self.dragged = p
                    break
        elif event.type == pygame.MOUSEMOTION and self.dragged:
            self.dragged.pos = list(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.dragged:
            p = self.dragged
            dist = math.hypot(p.pos[0] - p.target[0], p.pos[1] - p.target[1])
            if dist < 45:
                if p.idx == self.expected_idx:
                    p.pos = list(p.target)
                    p.placed = True
                    p.flash = 0.3
                    get_sound("collect.wav").play()
                    self.expected_idx += 1
                    if all(x.placed for x in self.pieces):
                        self.complete = True
                else:
                    self.failed = True
                    get_sound("miss.wav").play()
            else:
                p.pos = list(p.home)
                p.shake = 0.3
            p.dragging = False
            self.dragged = None

    def update(self, dt):
        for p in self.pieces:
            if p.flash > 0: p.flash -= dt
            if p.shake > 0: p.shake -= dt
        if self.complete: self.complete_timer += dt

    def draw(self, surface):
        draw_gradient_bg(surface, ONAM_DEEP, ONAM_BROWN)
        draw_text_shadow(surface, "\U0001f338  Pookalam", 30, 25, FONT_LG, GOLD)
        draw_text_centered(surface, "Drag the flower layers to build the Pookalam",
                           SCREEN_H - 50, FONT_SM, ONAM_LIGHT)
                           
        # Target silhouettes
        for p in self.pieces:
            if not p.placed: p.draw(surface, as_target=True)
            
        # Placed pieces (largest to smallest)
        for p in sorted(self.pieces, key=lambda x: -x.size):
            if p.placed: p.draw(surface)
            
        # Unplaced pieces
        for p in self.pieces:
            if not p.placed: p.draw(surface)
            
        if self.complete and self.complete_timer > 0.5:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 160))
            surface.blit(ov, (0, 0))
            draw_text_shadow(surface, "Pookalam Complete!",
                             SCREEN_W // 2 - 200, SCREEN_H // 2 - 40,
                             FONT_XL, GOLD)
            if self.complete_timer > 1.0:
                self.continue_btn.draw(surface)
                
        if self.failed:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((100, 0, 0, 160))
            surface.blit(ov, (0, 0))
            draw_text_shadow(surface, "Wrong Order!",
                             SCREEN_W // 2 - 130, SCREEN_H // 2 - 40,
                             FONT_XL, RED)
            self.retry_btn.draw(surface)
            
        draw_onam_border(surface)
