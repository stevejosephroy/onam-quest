# ── State Machine ────────────────────────────────────────────────────────────


class State:
    """Base class for every game state (boot, menu, each level, win screen)."""

    def __init__(self, machine):
        self.machine = machine          # back-reference to the StateMachine

    # -- lifecycle --
    def enter(self):
        """Called once when this state becomes active."""
        pass

    def exit(self):
        """Called once when leaving this state."""
        pass

    # -- per-frame --
    def handle_event(self, event):
        """Process a single pygame event."""
        pass

    def update(self, dt):
        """Update logic.  *dt* is seconds since last frame."""
        pass

    def draw(self, surface):
        """Render this state onto *surface*."""
        pass


class StateMachine:
    """Manages named states and routes the game-loop calls to the current one."""

    def __init__(self):
        self.states: dict[str, State] = {}
        self.current_state: State | None = None
        self.current_name: str | None = None

        # Shared bag of data every state can read / write
        self.game_data: dict = {
            "levels_cleared": set(),    # e.g. {1, 2, 3, 4}
            "scores": {},               # level_num -> int
        }

    # -- registration --
    def register(self, name: str, state: State):
        self.states[name] = state

    # -- transitions --
    def change_state(self, name: str):
        if self.current_state:
            self.current_state.exit()
        self.current_name = name
        self.current_state = self.states[name]
        self.current_state.enter()

    # -- delegation --
    def handle_event(self, event):
        if self.current_state:
            self.current_state.handle_event(event)

    def update(self, dt):
        if self.current_state:
            self.current_state.update(dt)

    def draw(self, surface):
        if self.current_state:
            self.current_state.draw(surface)
