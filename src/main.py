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
    current_level_number = 1

    overlay_timer = 0.0
    OVERLAY_HOLD = 2.5

    overlay_font_big = pygame.font.Font(None, 100)
    overlay_font_small = pygame.font.Font(None, 44)

    running = True
    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == 'menu':
                action = menu.handle_event(event)
                if action == 'level_1':
                    current_level_number = 1
                    level = Level(1)
                    player = Player(120, H - 200)
                    all_sprites = pygame.sprite.Group()
                    all_sprites.add(player)
                    state = 'game'
                    clock.tick()
                elif action == 'level_2':
                    current_level_number = 2
                    level = Level(2)
                    player = Player(W // 2, level.world_height - 80)
                    all_sprites = pygame.sprite.Group()
                    all_sprites.add(player)
                    state = 'game'
                    clock.tick()
                elif action == 'quit':
                    running = False

            elif state == 'game':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.jump()
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        player.try_dash(player.facing)

            elif state in ('win', 'dead'):
                if event.type == pygame.KEYDOWN:
                    state = 'menu'
                    overlay_timer = 0.0

        if state == 'menu':
            menu.update(pygame.mouse.get_pos())
            menu.draw(screen)

        elif state == 'game':
            level.update(player, dt)
            all_sprites.update(dt, level)

            if level.check_spike_collision(player.hitbox):
                player.hurt(player.facing)

            if level.check_goal_collision(player.hitbox):
                state = 'win'
                overlay_timer = 0.0

            if player.hitbox.top > level.world_height + 200:
                state = 'dead'
                overlay_timer = 0.0

            screen.fill((200, 220, 255))
            level.draw(screen)

            scroll_y = int(level.scroll_y) if current_level_number == 2 else 0
            player.draw_trail(screen, level.scroll, scroll_y)
            player.draw_stamina_bar(screen, level.scroll, scroll_y)
            # player.draw_debug(dt, screen, level.scroll, scroll_y)

            player_screen_rect = player.rect.copy()
            player_screen_rect.x -= int(level.scroll)
            player_screen_rect.y -= scroll_y
            screen.blit(player.image, player_screen_rect)

        elif state == 'win':
            overlay_timer += dt
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            title_surf = overlay_font_big.render("YOU WIN!", True, (100, 255, 180))
            sub_surf = overlay_font_small.render("Press any key to return to menu", True, (220, 220, 220))
            screen.blit(title_surf, title_surf.get_rect(center=(W // 2, H // 2 - 40)))
            screen.blit(sub_surf, sub_surf.get_rect(center=(W // 2, H // 2 + 50)))
            if overlay_timer >= OVERLAY_HOLD:
                state = 'menu'
                overlay_timer = 0.0

        elif state == 'dead':
            overlay_timer += dt
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            title_surf = overlay_font_big.render("YOU DIED", True, (255, 80, 80))
            sub_surf = overlay_font_small.render("Press any key to try again", True, (220, 220, 220))
            screen.blit(title_surf, title_surf.get_rect(center=(W // 2, H // 2 - 40)))
            screen.blit(sub_surf, sub_surf.get_rect(center=(W // 2, H // 2 + 50)))
            if overlay_timer >= OVERLAY_HOLD:
                state = 'menu'
                overlay_timer = 0.0

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
