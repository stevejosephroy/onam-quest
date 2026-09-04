# ── Escape Pathalam — Main Entry Point ───────────────────────────────────────
"""
Run with:  python main.py
Requires:  pip install pygame
"""
import pygame
import sys
from config import SCREEN_W, SCREEN_H, FPS, TITLE, BLACK
from src.state_machine import StateMachine
from src.boot_state import BootState
from src.menu_state import MenuState
from src.level1_pookalam import Level1Pookalam
from src.level2_sadya import Level2Sadya
from src.level3_vallam import Level3VallamState
from src.level4_thiruvathira import Level4ThiruvathiraState
from src.level5_final import FinalState
from src.win_screen import WinState
from src.game_over import GameOverState
from src.intro_state import IntroState
from src.instruction_state import InstructionState


import asyncio

async def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Escape Pathalam - Onam Quest")
    clock = pygame.time.Clock()

    sm = StateMachine()
    sm.game_data["lives"] = 5
    
    sm.register("boot", BootState(sm))
    sm.register("intro", IntroState(sm))
    sm.register("instruction", InstructionState(sm))
    sm.register("menu", MenuState(sm))
    sm.register("level1", Level1Pookalam(sm))
    sm.register("level2", Level2Sadya(sm))
    sm.register("level3", Level3VallamState(sm))
    sm.register("level4", Level4ThiruvathiraState(sm))
    sm.register("level5", FinalState(sm))
    sm.register("win", WinState(sm))
    sm.register("game_over", GameOverState(sm))
    sm.change_state("boot")

    try:
        pygame.mixer.music.load("assets/bgm.wav")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except:
        pass

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            sm.handle_event(event)
        sm.update(dt)
        screen.fill(BLACK)
        sm.draw(screen)
        pygame.display.flip()
        await asyncio.sleep(0) # Required for WebAssembly (pygbag)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())
