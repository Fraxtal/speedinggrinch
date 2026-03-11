import sys
import pygame
from level import Level
from player import Player


def main():
    pygame.init()
    W, H = 1280, 720
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption('speedinggrinch')
    clock = pygame.time.Clock()

    level = Level()
    player = Player(120, H - 200)

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    # dash in facing direction
                    facing = getattr(player, 'facing', 1)
                    player.try_dash(facing)

        all_sprites.update(dt, level)

        screen.fill((200, 220, 255))
        level.draw(screen)
        all_sprites.draw(screen)
        player.draw_trail(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
