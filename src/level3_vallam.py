# ── Level 3 — Vallam Kali (Boat Race) ──────────────────────────────────────────
import pygame, math, random
from src.state_machine import State
from src.ui_helpers import (
    get_font, FancyButton, draw_gradient_bg, draw_text_centered,
    draw_text_shadow, draw_onam_border,
)
from src.effects import ScreenShake
from config import *

class Level3VallamState(State):
    def enter(self):
        self.boat_x = SCREEN_W // 2
        self.boat_y = SCREEN_H - 100
        self.boat_w = 20
        self.boat_h = 140
        self.boat_speed = 400
        
        self.rocks = []
        self.rock_spawn_timer = 0.0
        self.rock_speed = 300
        
        self.distance = 0
        self.target_distance = 10000
        
        self.water_offset = 0.0
        
        self.failed = False
        self.complete = False
        self.shake = ScreenShake()
        
        self.cont_btn = FancyButton("Continue", SCREEN_W // 2, SCREEN_H // 2 + 60)
        self.retry_btn = FancyButton("Retry", SCREEN_W // 2, SCREEN_H // 2 + 60, fill=(10, 30, 80), border=RED)

    def exit(self): pass

    def handle_event(self, event):
        if self.complete:
            if self.cont_btn.handle_event(event):
                self.machine.game_data["levels_cleared"].add(3)
                self.machine.change_state("menu")
            return
        if self.failed:
            if self.retry_btn.handle_event(event):
                self.machine.game_data["lives"] -= 1
                if self.machine.game_data["lives"] <= 0:
                    self.machine.change_state("game_over")
                else:
                    self.machine.change_state("level3")
            return

    def update(self, dt):
        self.shake.update(dt)
        if self.complete or self.failed:
            return
            
        self.water_offset = (self.water_offset + dt * self.rock_speed) % 40
            
        keys = pygame.key.get_pressed()
        move_left = keys[pygame.K_LEFT]
        move_right = keys[pygame.K_RIGHT]
        
        # Mobile touch support
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            if mx < SCREEN_W // 2:
                move_left = True
            else:
                move_right = True

        if move_left:
            self.boat_x -= self.boat_speed * dt
        if move_right:
            self.boat_x += self.boat_speed * dt
            
        # Clamp boat
        self.boat_x = max(100, min(SCREEN_W - 100, self.boat_x))
        
        # Advance distance
        self.distance += self.rock_speed * dt
        if self.distance >= self.target_distance + 200:
            self.complete = True
            return
            
        # Spawn rocks (stop spawning after finish line)
        if self.distance < self.target_distance:
            self.rock_spawn_timer -= dt
            if self.rock_spawn_timer <= 0:
                rx = random.randint(100, SCREEN_W - 100)
                rr = random.randint(20, 40)
                self.rocks.append({"x": rx, "y": -50, "r": rr})
                self.rock_spawn_timer = random.uniform(0.4, 0.9)
            
        # Update rocks & check collisions
        boat_rect = pygame.Rect(self.boat_x - self.boat_w // 2, self.boat_y - self.boat_h // 2, self.boat_w, self.boat_h)
        
        for r in self.rocks:
            r["y"] += self.rock_speed * dt
            # Circular collision approx
            near_x = max(boat_rect.left, min(r["x"], boat_rect.right))
            near_y = max(boat_rect.top, min(r["y"], boat_rect.bottom))
            dist = math.hypot(near_x - r["x"], near_y - r["y"])
            if dist < r["r"] - 5:
                self.failed = True
                self.shake.trigger(10, 0.4)
                from src.asset_loader import get_sound
                get_sound("hit.wav").play()
                
        # Remove offscreen rocks
        self.rocks = [r for r in self.rocks if r["y"] < SCREEN_H + 100]
        
        # Increase difficulty slightly over time
        self.rock_speed += dt * 5

    def draw(self, surface):
        draw_gradient_bg(surface, (10, 40, 80), (20, 80, 140))
        
        # Draw water waves
        for y in range(int(self.water_offset) - 40, SCREEN_H, 40):
            for x in range(0, SCREEN_W, 60):
                pygame.draw.arc(surface, WATER_LIGHT, (x, y, 50, 20), 0, math.pi, 2)
                
        # Draw river banks
        pygame.draw.rect(surface, (30, 80, 20), (0, 0, 50, SCREEN_H))
        pygame.draw.rect(surface, (30, 80, 20), (SCREEN_W - 50, 0, 50, SCREEN_H))
        
        if self.shake.timer > 0:
            ox, oy = self.shake.get_offset()
            surface.scroll(int(ox), int(oy))
            
        # Draw Finish Line
        finish_y = int(self.boat_y - (self.target_distance - self.distance))
        if finish_y > -100:
            # Checkered pattern
            for x in range(50, SCREEN_W - 50, 40):
                pygame.draw.rect(surface, WHITE, (x, finish_y, 20, 20))
                pygame.draw.rect(surface, BLACK, (x + 20, finish_y, 20, 20))
                pygame.draw.rect(surface, BLACK, (x, finish_y + 20, 20, 20))
                pygame.draw.rect(surface, WHITE, (x + 20, finish_y + 20, 20, 20))
            draw_text_shadow(surface, "FINISH", SCREEN_W // 2 - 45, finish_y - 30, FONT_MD, GOLD)
            
        # Draw Rocks
        for r in self.rocks:
            rx, ry, rr = int(r["x"]), int(r["y"]), int(r["r"])
            pygame.draw.circle(surface, (80, 80, 80), (rx, ry), rr)
            pygame.draw.circle(surface, (100, 100, 100), (rx - rr//4, ry - rr//4), rr//2)
            
        # Draw Boat (Chundan Vallam)
        bx, by = int(self.boat_x), int(self.boat_y)
        bw, bh = self.boat_w, self.boat_h
        pts = [
            (bx, by - bh//2 - 40), # Stern (curved up)
            (bx + bw//2, by - bh//2), 
            (bx + bw//2, by + bh//2), 
            (bx, by + bh//2 + 30), # Bow (pointed)
            (bx - bw//2, by + bh//2),
            (bx - bw//2, by - bh//2)
        ]
        pygame.draw.polygon(surface, (100, 50, 20), pts)
        pygame.draw.polygon(surface, GOLD, pts, 2)
        
        # Draw rowers
        for i in range(5):
            ry = by - bh//2 + 20 + i * 20
            pygame.draw.circle(surface, WHITE, (bx - 5, ry), 4)
            pygame.draw.circle(surface, WHITE, (bx + 5, ry + 10), 4)
            # Oars
            pygame.draw.line(surface, (150, 100, 50), (bx - 5, ry), (bx - 20, ry + 10), 2)
            pygame.draw.line(surface, (150, 100, 50), (bx + 5, ry + 10), (bx + 20, ry + 20), 2)
            
        # UI
        display_dist = min(int(self.distance), self.target_distance)
        draw_text_shadow(surface, f"Distance: {display_dist} / {self.target_distance}", 20, 20, FONT_MD, WHITE)
        
        if self.complete:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 160))
            surface.blit(ov, (0, 0))
            draw_text_shadow(surface, "Race Finished!", SCREEN_W // 2 - 130, SCREEN_H // 2 - 40, FONT_XL, GOLD)
            self.cont_btn.draw(surface)
        elif self.failed:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((100, 0, 0, 160))
            surface.blit(ov, (0, 0))
            draw_text_shadow(surface, "CRASH!", SCREEN_W // 2 - 80, SCREEN_H // 2 - 40, FONT_XL, RED)
            self.retry_btn.draw(surface)
            
        draw_onam_border(surface)
