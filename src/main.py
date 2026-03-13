import pygame
import sys
import os
from player import Player
from level import Level
from menu import MainMenu

def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    
    W, H = 1280, 720
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption('Speeding Grinch')
    clock = pygame.time.Clock()
    
    menu = MainMenu(W, H)
    state = 'menu'
    level, player, all_sprites = None, None, None

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        if dt > 0.1: dt = 0.016

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if state == 'menu':
                action = menu.handle_event(event)
                if action and action.startswith('level'):
                    level = Level(1 if action == 'level_1' else 2)
                    player = Player(200, H - 100)
                    all_sprites = pygame.sprite.Group(player)
                    state = 'game'
                elif action == 'quit':
                    running = False
            
            elif state == 'game':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE: player.jump()
                    if event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]: player.try_dash(player.facing)
                    if event.key == pygame.K_ESCAPE:
                        menu.submenu = "main"
                        state = 'menu'

        if state == 'menu':
            menu.update(pygame.mouse.get_pos())
            menu.draw(screen)
            
        elif state == 'game':
            # 1. Update everything
            player.update(dt, level)
            level.update(player.vel.x, dt)
            
            # 2. DRAWING ORDER (Do not change this)
            level.draw(screen)           # FIRST: Background
            player.draw_trail(screen)    # SECOND: Ghost Trail
            screen.blit(player.image, player.rect) # THIRD: Character

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()