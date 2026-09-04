# ── Visual Effects ────────────────────────────────────────────────────────────
import pygame
import random
import math
from config import (
    SCREEN_W, SCREEN_H, BLACK,
    GOLD, ORANGE, PETAL_PINK, PETAL_YELLOW, PETAL_ORANGE,
    PETAL_RED, PETAL_WHITE, KERALA_GREEN, WHITE,
)


# ── Glitch Effect ────────────────────────────────────────────────────────────

class GlitchEffect:
    """Displaces random horizontal slices of the screen buffer."""

    def __init__(self, intensity=5):
        self.intensity = intensity
        self.active = False
        self.slices: list[tuple[int, int, int]] = []
        self.timer = 0.0

    def trigger(self, duration=0.1):
        self.active = True
        self.timer = duration
        self._gen()

    def set_continuous(self, on: bool):
        """Keep glitching every frame (for final level)."""
        self.active = on
        if on:
            self.timer = 999
            self._gen()

    def _gen(self):
        self.slices = []
        for _ in range(random.randint(3, 8)):
            y = random.randint(0, SCREEN_H)
            h = random.randint(2, 30)
            off = random.randint(-self.intensity * 3, self.intensity * 3)
            self.slices.append((y, h, off))

    def update(self, dt):
        if not self.active:
            return
        self.timer -= dt
        if self.timer <= 0:
            self.active = False
            self.slices = []
        elif random.random() < 0.35:
            self._gen()

    def apply(self, surface: pygame.Surface):
        if not self.active or not self.slices:
            return
        for y, h, off in self.slices:
            if y >= SCREEN_H:
                continue
            h = min(h, SCREEN_H - y)
            if h <= 0:
                continue
            strip = surface.subsurface(pygame.Rect(0, y, SCREEN_W, h)).copy()
            surface.fill(BLACK, (0, y, SCREEN_W, h))
            surface.blit(strip, (off, y))


# ── Screen Shake ─────────────────────────────────────────────────────────────

class ScreenShake:
    """Offsets the entire draw to simulate impact."""

    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0
        self.timer = 0.0
        self.intensity = 0

    def trigger(self, intensity=8, duration=0.3):
        self.intensity = intensity
        self.timer = duration

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
            self.offset_x = random.randint(-self.intensity, self.intensity)
            self.offset_y = random.randint(-self.intensity, self.intensity)
        else:
            self.offset_x = 0
            self.offset_y = 0

    def get_offset(self):
        return self.offset_x, self.offset_y


# ── Crack Overlay ────────────────────────────────────────────────────────────

class CrackOverlay:
    """Red fracture lines that spread across the screen as intensity rises."""

    def __init__(self):
        self.cracks: list[list[tuple[int, int]]] = []
        self.intensity = 0.0      # 0 … 1

    def set_intensity(self, value: float):
        self.intensity = max(0.0, min(1.0, value))
        self._gen()

    def _gen(self):
        self.cracks = []
        n = int(self.intensity * 15)
        for _ in range(n):
            pts: list[tuple[int, int]] = [
                (random.randint(0, SCREEN_W), random.randint(0, SCREEN_H))
            ]
            for _ in range(random.randint(3, 8)):
                lx, ly = pts[-1]
                pts.append((lx + random.randint(-60, 60),
                            ly + random.randint(-60, 60)))
            self.cracks.append(pts)

    def draw(self, surface: pygame.Surface):
        if self.intensity <= 0:
            return
        for pts in self.cracks:
            if len(pts) >= 2:
                pygame.draw.lines(surface, (255, 0, 0), False, pts, 2)
            for p in pts:
                glow = pygame.Surface((20, 20), pygame.SRCALPHA)
                a = int(self.intensity * 60)
                pygame.draw.circle(glow, (255, 0, 0, a), (10, 10), 10)
                surface.blit(glow, (p[0] - 10, p[1] - 10))


# ── Particle System ──────────────────────────────────────────────────────────

class Particle:
    """Base particle — point with velocity, gravity, and fade."""

    def __init__(self, x, y, vx, vy, color, life=2.0, size=4):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = float(vx), float(vy)
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 80 * dt          # gravity
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def draw(self, surface: pygame.Surface):
        if not self.alive:
            return
        ratio = max(0.0, self.life / self.max_life)
        alpha = int(255 * ratio)
        s = max(1, int(self.size * ratio))
        dot = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
        pygame.draw.circle(dot, (*self.color[:3], alpha), (s, s), s)
        surface.blit(dot, (int(self.x) - s, int(self.y) - s))


class PetalParticle(Particle):
    """Flower petal — floats, spins, flutters."""

    def __init__(self, x, y):
        color = random.choice([PETAL_PINK, PETAL_YELLOW, PETAL_ORANGE,
                                PETAL_RED, PETAL_WHITE, GOLD])
        super().__init__(x, y,
                         random.uniform(-50, 50), random.uniform(-100, 20),
                         color,
                         life=random.uniform(2.5, 5.0),
                         size=random.randint(4, 8))
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-180, 180)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 30 * dt
        self.vx += random.uniform(-20, 20) * dt   # flutter
        self.angle += self.spin * dt
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def draw(self, surface: pygame.Surface):
        if not self.alive:
            return
        ratio = max(0.0, self.life / self.max_life)
        alpha = int(255 * ratio)
        s = self.size
        petal = pygame.Surface((s * 3, s * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(petal, (*self.color[:3], alpha),
                            (0, 0, s * 3, s * 2))
        rotated = pygame.transform.rotate(petal, self.angle)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, rect)


class FireworkParticle(Particle):
    """Burst outward from a point at random angles."""

    def __init__(self, x, y, base_color=None):
        if base_color is None:
            base_color = random.choice([GOLD, ORANGE, PETAL_PINK,
                                         KERALA_GREEN, WHITE, PETAL_RED])
        angle = random.uniform(0, math.tau)
        speed = random.uniform(100, 300)
        super().__init__(x, y,
                         math.cos(angle) * speed, math.sin(angle) * speed,
                         base_color,
                         life=random.uniform(0.5, 1.5),
                         size=random.randint(2, 5))


class ParticleSystem:
    """Owns and ticks a list of particles."""

    def __init__(self):
        self.particles: list[Particle] = []

    def add(self, p: Particle):
        self.particles.append(p)

    def emit_firework(self, x, y, count=30, color=None):
        for _ in range(count):
            self.particles.append(FireworkParticle(x, y, color))

    def emit_petals(self, x, y, count=10):
        for _ in range(count):
            self.particles.append(PetalParticle(x, y))

    def emit_confetti(self, count=5):
        for _ in range(count):
            self.particles.append(PetalParticle(random.randint(0, SCREEN_W), -10))

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface: pygame.Surface):
        for p in self.particles:
            p.draw(surface)

    def clear(self):
        self.particles.clear()
