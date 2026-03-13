import sys
import pygame
from level import Level
from player import Player
from menu import MainMenu


def main():
    pygame.init()
    W, H = 1280, 720
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption('speedinggrinch')
    clock = pygame.time.Clock()
    
    menu = MainMenu(W, H)
    state = 'menu'
    
    level = None
    player = None
    all_sprites = None

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if state == 'menu':
                action = menu.handle_event(event)
                if action == 'start':
                    state = 'game'
                    level = Level() 
                    player = Player(120, H - 200)
                    clock.tick()
                    all_sprites = pygame.sprite.Group()
                    all_sprites.add(player)
                elif action == 'quit':
                    running = False
            
            elif state == 'game':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.jump()
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        facing = getattr(player, 'facing', 1)
                        player.try_dash(facing)
        
        if state == 'menu':
            menu.update(pygame.mouse.get_pos())
            menu.draw(screen)
        elif state == 'game':
            all_sprites.update(dt, level)
            screen.fill((200, 220, 255))
            level.draw(screen)
            player.draw_trail(screen)
            all_sprites.draw(screen)
            player.draw_debug(dt, screen)
        
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
