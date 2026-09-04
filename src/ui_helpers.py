# ── UI Helpers — Festival + Pathalam Styles ──────────────────────────────────
import pygame
import math
from config import *

# ── Font cache ───────────────────────────────────────────────────────────────
_font_cache: dict = {}


def get_font(size: int, bold: bool = False, mono: bool = False) -> pygame.font.Font:
    name = FONT_MONO if mono else FONT_NAME
    key = (name, size, bold)
    if key not in _font_cache:
        try:
            font = pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            font = pygame.font.SysFont(FONT_FALLBACK, size, bold=bold)
        _font_cache[key] = font
    return _font_cache[key]


# ── Gradient surface (cached) ────────────────────────────────────────────────
_gradient_cache: dict = {}


def get_gradient(w: int, h: int, top: tuple, bot: tuple) -> pygame.Surface:
    key = (w, h, top, bot)
    if key not in _gradient_cache:
        surf = pygame.Surface((w, h))
        for y in range(h):
            r = y / max(h - 1, 1)
            c = tuple(int(top[i] + (bot[i] - top[i]) * r) for i in range(3))
            pygame.draw.line(surf, c, (0, y), (w, y))
        _gradient_cache[key] = surf
    return _gradient_cache[key]


def draw_gradient_bg(surface: pygame.Surface, top: tuple, bot: tuple):
    """Blit a cached vertical gradient onto the surface."""
    surface.blit(get_gradient(surface.get_width(), surface.get_height(), top, bot), (0, 0))


# ── Typewriter Text ──────────────────────────────────────────────────────────

class TypewriterText:
    """Reveals a string character-by-character."""

    def __init__(self, text, x, y, size=FONT_MD, color=GOLD,
                 speed=TYPEWRITER_SPEED, bold=False):
        self.full_text = text
        self.x, self.y = x, y
        self.color = color
        self.speed = speed
        self.font = get_font(size, bold=bold)
        self.timer = 0.0
        self.char_index = 0
        self.done = False

    def update(self, dt):
        if self.done:
            return
        self.timer += dt
        while self.timer >= self.speed and self.char_index < len(self.full_text):
            self.timer -= self.speed
            self.char_index += 1
        if self.char_index >= len(self.full_text):
            self.char_index = len(self.full_text)
            self.done = True

    def skip(self):
        self.char_index = len(self.full_text)
        self.done = True

    def draw(self, surface):
        vis = self.full_text[: self.char_index]
        rendered = self.font.render(vis, True, self.color)
        surface.blit(rendered, (self.x, self.y))


# ── Fancy Button ─────────────────────────────────────────────────────────────

class FancyButton:
    """Rounded-rect button with fill, border, hover glow, and shadow."""

    def __init__(self, text, cx, cy, w=240, h=55,
                 fill=(60, 30, 10), border=GOLD, text_color=ONAM_CREAM,
                 size=FONT_MD, hover_fill=ONAM_BROWN):
        self.text = text
        self.w, self.h = w, h
        self.fill = fill
        self.hover_fill = hover_fill
        self.border = border
        self.text_color = text_color
        self.font = get_font(size, bold=True)
        self.rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        self.hovered = False
        self.enabled = True

    def set_center(self, cx, cy):
        self.rect.center = (cx, cy)

    def handle_event(self, event) -> bool:
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface: pygame.Surface):
        r = self.rect
        fill = self.hover_fill if (self.hovered and self.enabled) else self.fill

        if not self.enabled:
            fill = (40, 40, 40)
            border = GRAY
            tc = GRAY
        else:
            border = self.border
            tc = self.text_color

        # Shadow
        shadow = pygame.Rect(r.x + 3, r.y + 3, r.w, r.h)
        pygame.draw.rect(surface, (0, 0, 0, 80), shadow, border_radius=10)
        # Fill
        pygame.draw.rect(surface, fill, r, border_radius=10)
        # Border
        pygame.draw.rect(surface, border, r, 2, border_radius=10)
        # Text
        txt = self.font.render(self.text, True, tc)
        surface.blit(txt, (r.centerx - txt.get_width() // 2,
                           r.centery - txt.get_height() // 2))


# ── Terminal-style button (for Pathalam level) ───────────────────────────────

class TerminalButton:
    """Clickable ``[ LABEL ]`` for the dark Pathalam screens."""

    def __init__(self, text, x, y, size=FONT_MD, color=RED,
                 hover_color=PETAL_RED):
        self.text = text
        self.display = f"[ {text} ]"
        self.font = get_font(size, mono=True)
        self.color = color
        self.hover_color = hover_color
        self._normal = self.font.render(self.display, True, self.color)
        self._hover = self.font.render(self.display, True, self.hover_color)
        self._dim = self.font.render(self.display, True, GRAY)
        self.rect = self._normal.get_rect(topleft=(x, y))
        self.hovered = False
        self.enabled = True

    def set_center(self, cx, cy):
        self.rect.center = (cx, cy)

    def handle_event(self, event) -> bool:
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface):
        if not self.enabled:
            surface.blit(self._dim, self.rect)
        elif self.hovered:
            surface.blit(self._hover, self.rect)
        else:
            surface.blit(self._normal, self.rect)


# ── Decorative helpers ───────────────────────────────────────────────────────

def draw_pookalam_deco(surface: pygame.Surface, cx: int, cy: int, radius: int,
                       alpha: int = 120):
    """Draw a decorative mini-pookalam (semi-transparent)."""
    s = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
    c = radius + 2
    n = len(POOKALAM_COLORS)
    for i in range(n - 1, -1, -1):
        r = int(radius * (n - i) / n)
        if r < 3:
            continue
        col = (*POOKALAM_COLORS[i], alpha)
        pygame.draw.circle(s, col, (c, c), r)
        pygame.draw.circle(s, (*POOKALAM_COLORS[i], min(255, alpha + 50)),
                           (c, c), r, 2)
    # Petal accents
    for angle_deg in range(0, 360, 45):
        a = math.radians(angle_deg)
        px = c + int(math.cos(a) * radius * 0.7)
        py = c + int(math.sin(a) * radius * 0.7)
        pygame.draw.circle(s, (255, 255, 200, alpha // 2), (px, py), 4)
    surface.blit(s, (cx - c, cy - c))


def draw_nilavilakku(surface: pygame.Surface, cx: int, by: int, h: int = 80):
    """Draw a simple traditional brass oil lamp."""
    # Base
    pygame.draw.rect(surface, LAMP_BRONZE, (cx - 15, by - 10, 30, 10))
    pygame.draw.rect(surface, LAMP_BRONZE, (cx - 20, by, 40, 6))
    # Stem
    pygame.draw.rect(surface, LAMP_BRONZE, (cx - 4, by - 10 - h, 8, h))
    # Cup
    pygame.draw.ellipse(surface, LAMP_BRONZE, (cx - 18, by - 15 - h, 36, 16))
    # Flame
    fy = by - 20 - h
    pygame.draw.polygon(surface, LAMP_FLAME,
                        [(cx, fy - 20), (cx - 6, fy), (cx + 6, fy)])
    pygame.draw.polygon(surface, LAMP_GLOW,
                        [(cx, fy - 14), (cx - 3, fy - 2), (cx + 3, fy - 2)])
    # Glow halo
    glow = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 200, 80, 40), (25, 25), 25)
    surface.blit(glow, (cx - 25, fy - 30))


def draw_scanlines(surface, alpha=20, spacing=3):
    """CRT scanlines (used for Pathalam level only)."""
    key = (surface.get_size(), alpha, spacing)
    if key not in _gradient_cache:
        ov = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for y in range(0, surface.get_height(), spacing):
            pygame.draw.line(ov, (0, 0, 0, alpha), (0, y),
                             (surface.get_width(), y))
        _gradient_cache[key] = ov
    surface.blit(_gradient_cache[key], (0, 0))


# ── Text convenience ─────────────────────────────────────────────────────────

def draw_text_centered(surface, text, y, size=FONT_MD, color=ONAM_CREAM,
                       bold=False):
    font = get_font(size, bold=bold)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(centerx=surface.get_width() // 2, y=y)
    surface.blit(rendered, rect)
    return rect


def draw_text(surface, text, x, y, size=FONT_MD, color=ONAM_CREAM,
              bold=False):
    font = get_font(size, bold=bold)
    rendered = font.render(text, True, color)
    surface.blit(rendered, (x, y))
    return rendered.get_rect(topleft=(x, y))


def draw_text_shadow(surface, text, x, y, size=FONT_MD, color=GOLD,
                     shadow_color=(0, 0, 0), offset=2, bold=True):
    """Text with a drop shadow for readability."""
    font = get_font(size, bold=bold)
    shadow = font.render(text, True, shadow_color)
    surface.blit(shadow, (x + offset, y + offset))
    rendered = font.render(text, True, color)
    surface.blit(rendered, (x, y))
    return rendered.get_rect(topleft=(x, y))


def draw_onam_border(surface, color=ONAM_GOLD, width=3, margin=8):
    """Decorative double-line border with corner flowers."""
    w, h = surface.get_size()
    m = margin
    pygame.draw.rect(surface, color, (m, m, w - 2 * m, h - 2 * m), width)
    pygame.draw.rect(surface, (*color, 120) if len(color) == 3 else color,
                     (m + 5, m + 5, w - 2 * m - 10, h - 2 * m - 10), 1)
    # Corner dots
    for cx, cy in [(m + 4, m + 4), (w - m - 4, m + 4),
                   (m + 4, h - m - 4), (w - m - 4, h - m - 4)]:
        pygame.draw.circle(surface, GOLD, (cx, cy), 5)
        pygame.draw.circle(surface, ONAM_ORANGE, (cx, cy), 3)
