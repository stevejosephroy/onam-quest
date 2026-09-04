import pygame, math, random
from src.state_machine import State
from src.ui_helpers import (
    get_font, TerminalButton, draw_gradient_bg, draw_text_centered,
    draw_text_shadow, draw_text, draw_scanlines, TypewriterText, draw_onam_border
)
from src.effects import GlitchEffect, ScreenShake, CrackOverlay
from src.asset_loader import get_spritesheet
from config import *

# Obstacle types
OBS_ROCK   = 0   # ground
OBS_FIRE   = 1   # ground
OBS_BAT    = 2   # aerial
OBS_STALA  = 3   # aerial


class _Maveli:
    """The king trying to escape Pathalam."""

    def __init__(self):
        self.x = 150
        self.y = float(RUNNER_GROUND_Y)
        self.vy = 0.0
        self.on_ground = True
        self.ducking = False
        self.run_frame = 0
        self.run_timer = 0.0
        self.invincible = 0.0
        self.w, self.h = 40, 80
        self.frames = get_spritesheet("maveli_run.jpg", 2, 2, scale_each=(100, 100))

    def jump(self):
        if self.on_ground and not self.ducking:
            self.vy = RUNNER_JUMP_VEL
            self.on_ground = False
            from src.asset_loader import get_sound
            get_sound("jump.wav").play()

    def duck(self, active: bool):
        if self.on_ground:
            self.ducking = active
            self.h = 40 if active else 80

    def update(self, dt):
        if not self.on_ground:
            self.vy += RUNNER_GRAVITY * dt
            self.y += self.vy * dt
            if self.y >= RUNNER_GROUND_Y:
                self.y = RUNNER_GROUND_Y
                self.vy = 0
                self.on_ground = True
        if self.invincible > 0:
            self.invincible -= dt
        self.run_timer += dt
        if self.run_timer > 0.12:
            self.run_timer = 0
            self.run_frame = (self.run_frame + 1) % 4

    def get_rect(self) -> pygame.Rect:
        top = int(self.y) - self.h
        return pygame.Rect(self.x - self.w // 2, top, self.w, self.h)

    def draw(self, surface):
        if self.invincible > 0 and int(self.invincible * 10) % 2 == 0:
            return

        x, y = self.x, int(self.y)
        frame = self.frames[self.run_frame]
        if self.ducking:
            frame = pygame.transform.scale(frame, (100, 50))
            rect = frame.get_rect(midbottom=(x, y))
        else:
            rect = frame.get_rect(midbottom=(x, y))
            
        surface.blit(frame, rect)


class _Obstacle:
    def __init__(self, kind, x):
        self.kind = kind
        self.x = float(x)
        if kind in (OBS_ROCK, OBS_FIRE):
            self.y = RUNNER_GROUND_Y
            self.w = 40 if kind == OBS_ROCK else 55
            self.h = 45 if kind == OBS_ROCK else 28
        else:
            self.y = RUNNER_GROUND_Y - 75
            self.w = 35
            self.h = 30

    def get_rect(self):
        return pygame.Rect(int(self.x) - self.w // 2,
                           int(self.y) - self.h, self.w, self.h)

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        if self.kind == OBS_ROCK:
            pts = [(x - 20, y), (x - 15, y - 40), (x + 5, y - 45),
                   (x + 20, y - 30), (x + 18, y)]
            pygame.draw.polygon(surface, PATH_ROCK, pts)
            pygame.draw.polygon(surface, PATH_ROCK_LT, pts, 2)
        elif self.kind == OBS_FIRE:
            pygame.draw.rect(surface, (40, 20, 10), (x - 25, y - 8, 50, 8))
            for i in range(5):
                fx = x - 20 + i * 10
                fh = random.randint(15, 30)
                pygame.draw.polygon(surface, PATH_FIRE_RED,
                                    [(fx, y - 8), (fx + 5, y - 8 - fh),
                                     (fx + 10, y - 8)])
                pygame.draw.polygon(surface, PATH_FIRE_YEL,
                                    [(fx + 2, y - 8), (fx + 5, y - 8 - fh // 2),
                                     (fx + 8, y - 8)])
        elif self.kind == OBS_BAT:
            pygame.draw.circle(surface, (30, 10, 40), (x, y - 15), 8)
            pygame.draw.polygon(surface, (50, 15, 60),
                                [(x - 8, y - 15), (x - 25, y - 28),
                                 (x - 20, y - 10)])
            pygame.draw.polygon(surface, (50, 15, 60),
                                [(x + 8, y - 15), (x + 25, y - 28),
                                 (x + 20, y - 10)])
        elif self.kind == OBS_STALA:
            pts = [(x - 10, y - self.h), (x, y), (x + 10, y - self.h)]
            pygame.draw.polygon(surface, PATH_ROCK, pts)
            pygame.draw.polygon(surface, PATH_ROCK_LT, pts, 1)


class FinalState(State):
    def enter(self):
        try:
            pygame.mixer.music.load("assets/bgm.wav")
            pygame.mixer.music.play(-1)
        except: pass
        self.maveli = _Maveli()
        self.obstacles = []
        self.spawn_timer = 0.0
        self.speed = float(RUNNER_SPEED)
        self.distance = 0.0
        self.hp = RUNNER_MAX_HP
        self.done = False
        self.success = False
        self.fail_screen = False
        self.fail_timer = 0.0
        self.elapsed = 0.0
        self.bg_off1 = 0.0
        self.bg_off2 = 0.0
        self.glitch = GlitchEffect(intensity=6)
        self.shake = ScreenShake()
        self.cracks = CrackOverlay()
        self.lava_off = 0.0
        self.fail_text = None
        self.retry_btn = TerminalButton("RETRY", 0, 0, FONT_LG, RED)
        self.retry_btn.set_center(SCREEN_W // 2, SCREEN_H // 2 + 60)
        self.retry_btn.enabled = False

    def exit(self):
        self.glitch.set_continuous(False)

    def handle_event(self, event):
        if self.fail_screen:
            if self.retry_btn.handle_event(event):
                self.machine.game_data["lives"] -= 1
                if self.machine.game_data["lives"] <= 0:
                    self.machine.change_state("game_over")
                else:
                    self.machine.change_state("level5")
            return
        if self.done: return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP):
                self.maveli.jump()
            elif event.key == pygame.K_DOWN:
                self.maveli.duck(True)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                self.maveli.duck(False)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if my < SCREEN_H // 2:
                self.maveli.jump()
            else:
                self.maveli.duck(True)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.maveli.duck(False)

    def update(self, dt):
        self.glitch.update(dt)
        self.shake.update(dt)
        self.elapsed += dt

        if self.fail_screen:
            self.fail_timer += dt
            if self.fail_timer > 1.5 and self.fail_text is None:
                self.fail_text = TypewriterText(
                    "PATHALAM CLAIMS YOU...", SCREEN_W // 2 - 180,
                    SCREEN_H // 2 - 40, FONT_LG, RED, 0.05)
            if self.fail_text: self.fail_text.update(dt)
            if self.fail_timer > 3.0: self.retry_btn.enabled = True
            return

        if self.done: return

        self.maveli.update(dt)
        self.speed = RUNNER_SPEED + self.distance * 0.08
        self.distance += self.speed * dt * 0.01

        self.bg_off1 += self.speed * 0.1 * dt
        self.bg_off2 += self.speed * 0.4 * dt
        self.lava_off += self.speed * 0.6 * dt

        if self.distance < RUNNER_WIN_DIST:
            self.spawn_timer += dt
            spawn_interval = max(0.6, 1.5 - self.distance * 0.0005)
            if self.spawn_timer >= spawn_interval:
                self.spawn_timer = 0
                kind = random.choices([OBS_ROCK, OBS_FIRE, OBS_BAT, OBS_STALA],
                                      weights=[3, 2, 2, 1])[0]
                self.obstacles.append(_Obstacle(kind, SCREEN_W + 60))
        elif getattr(self, "portal_x", None) is None:
            self.portal_x = SCREEN_W + 100

        for o in self.obstacles: o.x -= self.speed * dt
        self.obstacles = [o for o in self.obstacles if o.x > -60]

        if self.maveli.invincible <= 0:
            mr = self.maveli.get_rect()
            for o in self.obstacles:
                if mr.colliderect(o.get_rect()):
                    self.hp -= 1
                    self.maveli.invincible = 1.5
                    self.shake.trigger(12, 0.3)
                    self.glitch.trigger(0.2)
                    self.cracks.set_intensity(1.0 - self.hp / RUNNER_MAX_HP)
                    from src.asset_loader import get_sound
                    get_sound("hit.wav").play()
                    break

        if getattr(self, "portal_x", None) is not None:
            self.portal_x -= self.speed * dt
            if self.maveli.x >= self.portal_x - 30:
                self.done = True
                self.success = True
                self.machine.game_data["levels_cleared"].add(5)
                self.machine.change_state("win")
        elif self.hp <= 0:
            self.done = True
            self.fail_screen = True
            self.fail_timer = 0.0
            try:
                pygame.mixer.music.load("assets/bgm_creepy.wav")
                pygame.mixer.music.play(-1)
            except: pass

    def draw(self, surface: pygame.Surface):
        if self.fail_screen:
            surface.fill(BLACK)
            if self.fail_text: self.fail_text.draw(surface)
            if self.fail_timer > 3.0: self.retry_btn.draw(surface)
            self.cracks.draw(surface)
            return

        draw_gradient_bg(surface, PATH_SKY_TOP, PATH_SKY_BOT)
        for i in range(5):
            px = ((i * 300 - self.bg_off1) % (SCREEN_W + 300)) - 300
            pygame.draw.polygon(surface, PATH_PURPLE,
                                [(px, SCREEN_H), (px + 150, 150), (px + 300, SCREEN_H)])

        for i in range(8):
            px = ((i * 150 - self.bg_off2) % (SCREEN_W + 150)) - 150
            pygame.draw.rect(surface, (30, 10, 15),
                             (px + 20, 250 + (i % 3) * 30, 60, SCREEN_H))

        gy = RUNNER_GROUND_Y
        pygame.draw.rect(surface, PATH_ROCK, (0, gy, SCREEN_W, SCREEN_H - gy))
        pygame.draw.line(surface, PATH_ROCK_LT, (0, gy), (SCREEN_W, gy), 4)

        for x in range(0, SCREEN_W, 40):
            y_wave = SCREEN_H - 20 + math.sin((x + self.lava_off) * 0.05) * 8
            pygame.draw.circle(surface, PATH_FIRE_RED, (x, int(y_wave)), 25)
            pygame.draw.circle(surface, PATH_FIRE_YEL, (x, int(y_wave) - 5), 15)

        if getattr(self, "portal_x", None) is not None:
            px = int(self.portal_x)
            py = RUNNER_GROUND_Y - 50
            t = self.elapsed * 5
            for r in range(80, 0, -10):
                color = (
                    int(100 + 100 * math.sin(t + r*0.1)),
                    int(200 + 55 * math.sin(t*1.3 + r*0.2)),
                    int(100 + 100 * math.cos(t*0.7 + r*0.1))
                )
                pygame.draw.circle(surface, color, (px, py), r)
            draw_text_shadow(surface, "KERALA", px - 45, py - 110, FONT_MD, WHITE)

        for o in self.obstacles: o.draw(surface)
        self.maveli.draw(surface)
        
        draw_text_shadow(surface, f"Distance: {int(self.distance)}m", 20, 20, FONT_MD, WHITE)
        for i in range(RUNNER_MAX_HP):
            c = GOLD if i < self.hp else (40, 40, 40)
            pygame.draw.rect(surface, c, (SCREEN_W - 120 + i * 35, 20, 30, 10))

        if self.shake.timer > 0:
            ox, oy = self.shake.get_offset()
            surface.scroll(int(ox), int(oy))
            
        self.cracks.draw(surface)
        draw_onam_border(surface)
