import pygame
import os
from level import Level
from player import Player
from menu import MainMenu, StoryScroll
from enemy import Enemy

def main():
    pygame.init()
    W, H = 1280, 720
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption('speedinggrinch')
    clock = pygame.time.Clock()
    menu = MainMenu(W, H)
    state = 'menu'
    story = None
    pending_level = None
    level = None
    player = None
    all_sprites = None
    current_level_number = 1
    overlay_timer = 0.0
    OVERLAY_HOLD = 2.5
    prev_touching_machine = False
    enemies = []
    levels_complete = set()
    overlay_font_big = pygame.font.Font(None, 100)
    overlay_font_small = pygame.font.Font(None, 44)
    running = True
    pygame.mixer.music.load(os.path.join("assets", "Sound", "menu_music.mp3"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if state == 'menu':
                action = menu.handle_event(event)
                if action == 'level_1':
                    story = StoryScroll(W, H)
                    pending_level = 1
                    state = 'story'
                    prev_touching_machine = False
                elif action == 'level_2':
                    story = StoryScroll(W, H)
                    pending_level = 2
                    state = 'story'
                    prev_touching_machine = False
                    prev_touching_machine = False
                elif action == 'quit':
                    running = False
            elif state == 'story':
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    story.dismiss()
            elif state == 'game':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.jump()
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        player.try_dash(player.facing)
            elif state in ('win', 'dead', 'caught'):
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    state = 'menu'
                    overlay_timer = 0.0
                    menu = MainMenu(W, H, both_complete=(levels_complete == {1, 2}))
                    pygame.mixer.music.load(os.path.join("assets", "Sound", "menu_music.mp3"))
                    pygame.mixer.music.play(-1)
        if state == 'menu':
            menu.update(pygame.mouse.get_pos(), dt)
            menu.draw(screen)
        elif state == 'story':
            story.update(dt)
            menu.bg.draw(screen)  # keep the scrolling bg behind the scroll
            story.draw(screen)
            if story.done:
                current_level_number = pending_level
                level = Level(pending_level)
                player = Player(120, H - 200)
                all_sprites = pygame.sprite.Group()
                all_sprites.add(player)
                enemies = [Enemy(x, plat) for x, plat in level.enemies]
                clock.tick()
                pygame.mixer.music.load(os.path.join("assets", "Sound", "game_music.mp3"))
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
                state = 'game'
        elif state == 'game':
            level.update(player, dt)
            all_sprites.update(dt, level)
            for enemy in enemies:
                enemy.update(dt)
                if enemy.can_see(player.hitbox) and not player.dashing:
                    state = 'caught'
                    overlay_timer = 0.0
                    break
            if level.check_spike_collision(player.hitbox):
                player.try_hurt(player.facing)

            touching_machine = level.check_machine_collision(player.hitbox)
            if touching_machine and not prev_touching_machine and not player.dashing:
                player.vel.x *= 0.5
                player.try_hurt(player.facing)
            prev_touching_machine = touching_machine
            if level.check_goal_collision(player.hitbox):
                levels_complete.add(current_level_number)
                state = 'win'
                overlay_timer = 0.0

            if player.hitbox.top > level.world_height + 200:
                state = 'dead'
                overlay_timer = 0.0
            screen.fill((200, 220, 255))
            level.draw(screen)
            player.draw_trail(screen, level.scroll)
            player.draw_stamina_bar(screen, level.scroll)
            for enemy in enemies:
                enemy.draw(screen, level.scroll)
            player_screen_rect = player.rect.copy()
            player_screen_rect.x -= int(level.scroll)
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
                menu = MainMenu(W, H, both_complete=(levels_complete == {1, 2}))
                pygame.mixer.music.load(os.path.join("assets", "Sound", "menu_music.mp3"))
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
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
        elif state == 'caught':
            overlay_timer += dt
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            title_surf = overlay_font_big.render("CAUGHT!", True, (255, 200, 0))
            sub_surf = overlay_font_small.render("Press any key to return to menu", True, (220, 220, 220))
            screen.blit(title_surf, title_surf.get_rect(center=(W // 2, H // 2 - 40)))
            screen.blit(sub_surf, sub_surf.get_rect(center=(W // 2, H // 2 + 50)))
            if overlay_timer >= OVERLAY_HOLD:
                state = 'menu'
                overlay_timer = 0.0
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()