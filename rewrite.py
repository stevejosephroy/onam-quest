import sys

# Read the top part
lines = open('src/level5_final.py').readlines()[:126]
top_part = "".join(lines)

new_class = """class FinalState(State):
    def enter(self):
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

    def draw(self, surface: pygame.Surface):
        if self.fail_screen:
            surface.fill(BLACK)
            if self.fail_text: self.fail_text.draw(surface)
            if self.fail_timer > 3.0: self.retry_btn.draw(surface)
            self.cracks.draw(surface)
            return

        draw_gradient_bg(surface, PATH_BG_TOP, PATH_BG_BOT)
        for i in range(5):
            px = ((i * 300 - self.bg_off1) % (SCREEN_W + 300)) - 300
            pygame.draw.polygon(surface, PATH_BG_MID,
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
"""

open('src/level5_final.py', 'w').write(top_part + new_class)
