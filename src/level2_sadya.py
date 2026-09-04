import pygame, random, math
from src.state_machine import State
from src.ui_helpers import (
    get_font, FancyButton, draw_gradient_bg, draw_text_centered,
    draw_text_shadow, draw_onam_border, draw_text,
)
from src.asset_loader import get_image, get_sound
from config import *

_SLOT_LAYOUT = {
    "Pickle":  (-160, -60), "Papadam": (0, -80), "Payasam": (160, -60),
    "Sambar":  (-140,  40), "Rice":    (0,  50), "Avial":   (140,  40),
}
_DISH_VIS = {
    "Rice": ("food_rice.jpg", 50, 40), "Sambar": ("food_sambar.jpg", 30, 30),
    "Avial": ("food_avial.jpg", 30, 30), "Papadam": ("food_papadam.jpg", 40, 40),
    "Payasam": ("food_payasam.jpg", 25, 25), "Pickle": ("food_pickle.jpg", 20, 20),
}

class _Dish:
    def __init__(self, name, color, slot, start):
        self.name, self.color = name, color
        self.slot, self.home, self.pos = list(slot), list(start), list(start)
        self.placed = self.dragging = False
        self.flash = self.err = 0.0
        v = _DISH_VIS.get(name, ("food_rice.jpg", 20, 20))
        self.img_file, self.hw, self.hh = v
        self.img = get_image(self.img_file, scale=(self.hw * 2 + 10, self.hh * 2 + 10))

    def hit(self, mx, my):
        return abs(mx - self.pos[0]) < self.hw + 12 and abs(my - self.pos[1]) < self.hh + 12

    def draw_slot(self, surface):
        x, y = int(self.slot[0]), int(self.slot[1])
        col = ONAM_LIGHT if self.placed else (*ONAM_GOLD, 70)
        s = pygame.Surface((self.hw * 2 + 20, self.hh * 2 + 20), pygame.SRCALPHA)
        pygame.draw.circle(s, col, (self.hw + 10, self.hh + 10), self.hw + 5, 2)
        surface.blit(s, (x - self.hw - 10, y - self.hh - 10))
        f = get_font(FONT_SM - 3)
        lbl = f.render(self.name, True, ONAM_CREAM)
        surface.blit(lbl, (x - lbl.get_width() // 2, y + self.hh + 8))

    def draw(self, surface):
        x, y = int(self.pos[0]), int(self.pos[1])
        if self.err > 0:
            x += random.randint(-3, 3); y += random.randint(-3, 3)
        
        # Draw image
        rect = self.img.get_rect(center=(x, y))
        surface.blit(self.img, rect)
        
        if self.flash > 0:
            pygame.draw.circle(surface, GOLD, (x, y), self.hw + 6, 3)
        elif self.err > 0:
            pygame.draw.circle(surface, RED, (x, y), self.hw + 6, 3)
        elif self.placed:
            pygame.draw.circle(surface, GOLD, (x, y), self.hw + 4, 2)
            
        f = get_font(FONT_SM - 3, bold=True)
        lbl = f.render(self.name, True, (30, 20, 10))
        surface.blit(lbl, (x - lbl.get_width() // 2, y - 6))

class Level2Sadya(State):
    def enter(self):
        self.leaf_img = get_image("banana_leaf.jpg", scale=(750, 450))
        lcx, lcy = SCREEN_W // 3 + 20, SCREEN_H // 2 + 10
        self.leaf_center = (lcx, lcy)
        self.dishes: list[_Dish] = []
        ys = list(range(len(SADYA_DISHES)))
        random.shuffle(ys)
        for i, (name, color) in enumerate(SADYA_DISHES):
            off = _SLOT_LAYOUT[name]
            self.dishes.append(_Dish(name, color,
                                     (lcx + off[0], lcy + off[1]),
                                     (SCREEN_W - 130, 110 + ys[i] * 95)))
        self.dragged = None
        self.time_left = 20.0
        self.complete = self.failed = False
        self.end_timer = 0.0
        self.cont_btn = FancyButton("Continue", SCREEN_W // 2, SCREEN_H // 2 + 70)
        self.retry_btn = FancyButton("Retry", SCREEN_W // 2, SCREEN_H // 2 + 70,
                                     fill=(80, 10, 10), border=RED)

    def exit(self): pass

    def handle_event(self, event):
        if self.complete:
            if self.end_timer > 1.0 and self.cont_btn.handle_event(event):
                self.machine.game_data["levels_cleared"].add(2)
                self.machine.change_state("menu")
            return
        if self.failed:
            if self.end_timer > 1.0 and self.retry_btn.handle_event(event):
                self.machine.game_data["lives"] -= 1
                if self.machine.game_data["lives"] <= 0:
                    self.machine.change_state("game_over")
                else:
                    self.machine.change_state("level2")
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for d in reversed(self.dishes):
                if not d.placed and d.hit(*event.pos):
                    d.dragging = True; self.dragged = d; break
        elif event.type == pygame.MOUSEMOTION and self.dragged:
            self.dragged.pos = list(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.dragged:
            d = self.dragged
            dist = math.hypot(d.pos[0] - d.slot[0], d.pos[1] - d.slot[1])
            if dist < 45:
                d.pos = list(d.slot); d.placed = True; d.flash = 0.4
                get_sound("collect.wav").play()
                if all(x.placed for x in self.dishes): self.complete = True
            else:
                d.pos = list(d.home); d.err = 0.35
                get_sound("miss.wav").play()
            d.dragging = False; self.dragged = None

    def update(self, dt):
        if not self.complete and not self.failed:
            self.time_left -= dt
            if self.time_left <= 0: self.time_left = 0; self.failed = True
        for d in self.dishes:
            if d.flash > 0: d.flash -= dt
            if d.err > 0: d.err -= dt
        if self.complete or self.failed: self.end_timer += dt

    def draw(self, surface):
        draw_gradient_bg(surface, ONAM_DEEP, ONAM_BROWN)
        draw_text_shadow(surface, "\U0001f35b  Sadya", 30, 25, FONT_LG, GOLD)
        t = max(0, int(self.time_left))
        tc = RED if t < 10 else ONAM_CREAM
        draw_text(surface, f"Time: {t}s", SCREEN_W - 160, 30, FONT_MD, tc, True)

        # Banana leaf image
        lcx, lcy = self.leaf_center
        leaf_rect = self.leaf_img.get_rect(center=(lcx, lcy))
        surface.blit(self.leaf_img, leaf_rect)

        for d in self.dishes:
            if not d.placed: d.draw_slot(surface)
        for d in self.dishes:
            if d.placed: d.draw(surface)
        for d in self.dishes:
            if not d.placed: d.draw(surface)

        draw_text_centered(surface, "Drag dishes to the leaf", SCREEN_H - 50,
                           FONT_SM, ONAM_LIGHT)
        if (self.complete or self.failed) and self.end_timer > 0.5:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 160)); surface.blit(ov, (0, 0))
            if self.complete:
                draw_text_shadow(surface, "Sadya Complete!", SCREEN_W // 2 - 170,
                                 SCREEN_H // 2 - 40, FONT_XL, GOLD)
                if self.end_timer > 1.0: self.cont_btn.draw(surface)
            else:
                draw_text_shadow(surface, "Time's Up!", SCREEN_W // 2 - 120,
                                 SCREEN_H // 2 - 40, FONT_XL, RED)
                if self.end_timer > 1.0: self.retry_btn.draw(surface)
        draw_onam_border(surface)
