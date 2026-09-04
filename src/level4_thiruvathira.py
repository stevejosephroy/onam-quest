# ── Level 4 — Thiruvathira (Lamp-lit Dance Rhythm) ───────────────────────────
import pygame, math, random
from src.state_machine import State
from src.ui_helpers import (
    get_font, FancyButton, draw_gradient_bg, draw_text_centered,
    draw_text_shadow, draw_text, draw_nilavilakku,
)
from src.effects import ScreenShake
from src.asset_loader import get_spritesheet
from config import *

BEAT_COUNT = 25
WIN_SCORE  = 5000
BEAT_SPEED = 320


class Level4ThiruvathiraState(State):
    def __init__(self, machine):
        super().__init__(machine)
        # Load dancer frames (DALL-E generated a 2x2 grid)
        self.dancer_frames = get_spritesheet("dancer.jpg", 2, 2, scale_each=(160, 240))

    def enter(self):
        self.beat_interval = 60.0 / LEVEL4_BPM
        self.track_x = SCREEN_W // 2 + 80
        self.target_y = 580

        self.beats = []
        t = 2.0
        for _ in range(BEAT_COUNT):
            self.beats.append({"y": float(self.target_y - t * BEAT_SPEED),
                               "hit": False, "missed": False})
            t += random.choice([0.5, 1.0, 1.0, 1.5]) * self.beat_interval

        self.score = self.combo = 0
        self.feedback = ""
        self.fb_timer = self.elapsed = 0.0
        self.finished = self.win = False
        self.pose = 0
        self.dancer_lit = self.flash_line = self.clap_r = self.err_flash = 0.0
        self.shake = ScreenShake()
        self.cont_btn = FancyButton("Continue", SCREEN_W // 2, SCREEN_H // 2 + 100)
        self.retry_btn = FancyButton("Retry", SCREEN_W // 2, SCREEN_H // 2 + 100,
                                     fill=(60, 20, 10), border=LAMP_FLAME)

    def exit(self): pass

    def handle_event(self, event):
        if self.finished:
            if self.win and self.cont_btn.handle_event(event):
                self.machine.change_state("menu")
            elif not self.win and self.retry_btn.handle_event(event):
                self.machine.game_data["lives"] -= 1
                if self.machine.game_data["lives"] <= 0:
                    self.machine.change_state("game_over")
                else:
                    self.machine.change_state("level4")
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._hit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._hit()

    def _hit(self):
        best, bd = None, 999
        for b in self.beats:
            if b["hit"] or b["missed"]: continue
            d = abs(b["y"] - self.target_y)
            if d < bd: best, bd = b, d
        if best and bd <= 80:
            best["hit"] = True
            if bd <= 20:
                self.feedback = "PERFECT!"; self.combo += 1; self.score += 100 * self.combo
            elif bd <= 50:
                self.feedback = "GOOD"; self.combo += 1; self.score += 50 * self.combo
            else:
                self.feedback = "OK"; self.combo = 0
            self.fb_timer = 0.5; self.pose = (self.pose + 1) % 4
            self.dancer_lit = 0.35; self.clap_r = 10.0
            from src.asset_loader import get_sound
            get_sound("collect.wav").play()
        else:
            self.feedback = "MISS"; self.combo = 0; self.fb_timer = 0.5
            self.score = max(0, self.score - 100)
            self.shake.trigger(5, 0.2); self.err_flash = 0.15
            from src.asset_loader import get_sound
            get_sound("miss.wav").play()

    def update(self, dt):
        self.shake.update(dt)
        if self.finished: return
        self.elapsed += dt
        for attr in ("fb_timer", "dancer_lit", "flash_line", "err_flash"):
            v = getattr(self, attr)
            if v > 0: setattr(self, attr, v - dt)
        if self.clap_r > 0:
            self.clap_r += dt * 180
            if self.clap_r > 120: self.clap_r = 0
        done = True
        remaining_beats = 0
        for b in self.beats:
            if b["hit"] or b["missed"]: continue
            remaining_beats += 1
            b["y"] += BEAT_SPEED * dt
            if abs(b["y"] - self.target_y) < BEAT_SPEED * dt: self.flash_line = 0.1
            if b["y"] > self.target_y + 50:
                b["missed"] = True; self.combo = 0; self.feedback = "MISS"
                self.score = max(0, self.score - 100)
                self.fb_timer = 0.5; self.shake.trigger(4, 0.15); self.err_flash = 0.15
            else: done = False
            
        # Early fail check: can we still reach WIN_SCORE?
        max_possible = self.score
        c = self.combo
        for _ in range(remaining_beats):
            c += 1
            max_possible += 100 * c
            
        if max_possible < WIN_SCORE:
            self._finish(early_fail=True)
            return

        if done and self.elapsed > 3.0: self._finish()

    def _finish(self, early_fail=False):
        self.finished = True
        self.win = self.score >= WIN_SCORE and not early_fail
        if self.win:
            self.machine.game_data["levels_cleared"].add(4)
            self.machine.game_data["scores"][4] = max(
                self.score, self.machine.game_data["scores"].get(4, 0))

    def _draw_dancer(self, surface, x, y):
        frame = self.dancer_frames[self.pose]
        rect = frame.get_rect(center=(x, y - 50))
        surface.blit(frame, rect)
        
        if self.dancer_lit > 0:
            pygame.draw.circle(surface, LAMP_FLAME, (x, y - 50), 100, 2)

    def draw(self, surface):
        if self.err_flash > 0:
            draw_gradient_bg(surface, (60, 10, 5), (80, 30, 15))
        else:
            draw_gradient_bg(surface, LAMP_BG_TOP, LAMP_BG_BOT)

        # Lamps
        draw_nilavilakku(surface, 60, SCREEN_H - 30, 100)
        draw_nilavilakku(surface, SCREEN_W - 60, SCREEN_H - 30, 100)

        draw_text_shadow(surface, "\U0001f483  Thiruvathira", 20, 15, FONT_LG, LAMP_FLAME)
        draw_text(surface, f"Score: {self.score} / {WIN_SCORE}", SCREEN_W - 220, 20, FONT_MD, WHITE, True)
        draw_text(surface, f"Combo: x{self.combo}", SCREEN_W - 220, 48, FONT_MD, GOLD, True)

        if not self.finished:
            tx = self.track_x
            self._draw_dancer(surface, tx - 180, SCREEN_H // 2 + 20)
            # Track
            pygame.draw.line(surface, (255, 200, 100, 60), (tx, 80), (tx, SCREEN_H - 80), 1)
            # Target line
            tlc = WHITE if self.flash_line > 0 else LAMP_FLAME
            pygame.draw.line(surface, tlc, (tx - 45, self.target_y), (tx + 45, self.target_y), 3)
            # Clap burst
            if self.clap_r > 0:
                a = max(0, 255 - int(self.clap_r / 120 * 255))
                cs = pygame.Surface((260, 260), pygame.SRCALPHA)
                pygame.draw.circle(cs, (255, 200, 80, a), (130, 130), int(self.clap_r), 2)
                surface.blit(cs, (tx - 130, self.target_y - 130))
            # Beats
            for b in self.beats:
                if not b["hit"] and not b["missed"] and -10 < b["y"] < SCREEN_H + 10:
                    pygame.draw.circle(surface, LAMP_FLAME, (tx, int(b["y"])), 10)
                    pygame.draw.circle(surface, GOLD, (tx, int(b["y"])), 10, 2)
                    pygame.draw.circle(surface, WHITE, (tx, int(b["y"])), 4)
            if self.fb_timer > 0:
                fc = GOLD if "PERFECT" in self.feedback else (
                    WHITE if "GOOD" in self.feedback else RED)
                draw_text_centered(surface, self.feedback, self.target_y - 55, FONT_LG, fc)
            draw_text_centered(surface, "Press SPACE on the beat!", SCREEN_H - 30, FONT_SM, ONAM_CREAM)
        else:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 150)); surface.blit(ov, (0, 0))
            if self.win:
                draw_text_shadow(surface, "Dance Complete!", SCREEN_W // 2 - 180,
                                 SCREEN_H // 2 - 50, FONT_XL, GOLD)
                self.cont_btn.draw(surface)
            else:
                draw_text_shadow(surface, "FAILED!", SCREEN_W // 2 - 90,
                                 SCREEN_H // 2 - 50, FONT_XL, RED)
                draw_text_centered(surface, f"Score: {self.score} / {WIN_SCORE}",
                                   SCREEN_H // 2 + 10, FONT_MD, WHITE)
                self.retry_btn.draw(surface)
