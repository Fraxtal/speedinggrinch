import pygame
import os
from level import Level


class MenuBackground:
    SCROLL_SPEED = 180   # px per second
    FADE_DURATION = 1.2  # seconds to fade out / fade in

    def __init__(self, screen_width, screen_height):
        self.W = screen_width
        self.H = screen_height
        self.level = Level(1)
        self.max_scroll = self.level.world_width - screen_width
        self.scroll = 0.0
        self._fade_alpha = 0        # 0 = transparent overlay, 255 = black
        self._fading_out = False
        self._fading_in = False
        self._fade_surf = pygame.Surface((screen_width, screen_height))
        self._fade_surf.fill((0, 0, 0))

    def update(self, dt):
        fade_step = int(255 / self.FADE_DURATION * dt)

        if self._fading_out:
            self._fade_alpha = min(255, self._fade_alpha + fade_step)
            if self._fade_alpha >= 255:
                self.scroll = 0.0
                self._fading_out = False
                self._fading_in = True
            return

        if self._fading_in:
            self._fade_alpha = max(0, self._fade_alpha - fade_step)
            if self._fade_alpha <= 0:
                self._fading_in = False
            return

        self.scroll += self.SCROLL_SPEED * dt
        if self.scroll >= self.max_scroll:
            self.scroll = self.max_scroll
            self._fading_out = True

    def draw(self, surf):
        self.level.draw_bg_at(surf, self.scroll)
        if self._fade_alpha > 0:
            self._fade_surf.set_alpha(self._fade_alpha)
            surf.blit(self._fade_surf, (0, 0))


class MainMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.submenu = "main"
        self.bg = MenuBackground(screen_width, screen_height)

        # Load assets
        asset_path = 'main_menu'
        try:
            self.title = pygame.image.load(os.path.join(asset_path, 'menu_title.png')).convert_alpha()
            self.start_btn = pygame.image.load(os.path.join(asset_path, 'button_start.png')).convert_alpha()
            self.quit_btn = pygame.image.load(os.path.join(asset_path, 'button_quit.png')).convert_alpha()

            # Scale buttons
            self.start_btn = pygame.transform.scale(self.start_btn, (int(self.screen_width * 0.25), int(self.screen_height * 0.125)))
            self.quit_btn = pygame.transform.scale(self.quit_btn, (int(self.screen_width * 0.25), int(self.screen_height * 0.125)))
        except:
            self.title = pygame.Surface((400, 100), pygame.SRCALPHA)
            self.start_btn = pygame.Surface((200, 50))
            self.start_btn.fill((100, 100, 100))
            self.quit_btn = pygame.Surface((200, 50))
            self.quit_btn.fill((100, 100, 100))

        # Position elements
        self.title_rect = self.title.get_rect(center=(screen_width // 2, screen_height // 3))
        self.start_rect = self.start_btn.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
        self.quit_rect = self.quit_btn.get_rect(center=(screen_width // 2, screen_height // 2 + 170))

        # Level Selection Rects
        self.font = pygame.font.Font(None, 50)
        self.lvl1_rect = pygame.Rect(0, 0, 250, 60)
        self.lvl2_rect = pygame.Rect(0, 0, 250, 60)
        self.back_rect = pygame.Rect(0, 0, 250, 60)

        self.lvl1_rect.center = (screen_width // 2, screen_height // 2 - 20)
        self.lvl2_rect.center = (screen_width // 2, screen_height // 2 + 60)
        self.back_rect.center = (screen_width // 2, screen_height // 2 + 180)

        # Hover states
        self.start_hovered = False
        self.quit_hovered = False
        self.lvl1_hovered = False
        self.lvl2_hovered = False
        self.back_hovered = False
        self._prev_hovered = set()

        # SFX
        self.pop_sfx = pygame.mixer.Sound(os.path.join(asset_path, 'sfx', 'popsfx.mp3'))
        self._sfx_channel = pygame.mixer.find_channel()

    def _play_pop(self):
        if self._sfx_channel and not self._sfx_channel.get_busy():
            self._sfx_channel.play(self.pop_sfx)

    def update(self, mouse_pos, dt=0):
        self.bg.update(dt)
        self.start_hovered = self.start_rect.collidepoint(mouse_pos)
        self.quit_hovered = self.quit_rect.collidepoint(mouse_pos)
        self.lvl1_hovered = self.lvl1_rect.collidepoint(mouse_pos)
        self.lvl2_hovered = self.lvl2_rect.collidepoint(mouse_pos)
        self.back_hovered = self.back_rect.collidepoint(mouse_pos)

        now_hovered = {k for k, v in {
            'start': self.start_hovered, 'quit': self.quit_hovered,
            'lvl1': self.lvl1_hovered, 'lvl2': self.lvl2_hovered,
            'back': self.back_hovered,
        }.items() if v}
        if now_hovered - self._prev_hovered:
            self._play_pop()
        self._prev_hovered = now_hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.submenu == "main":
                if self.start_rect.collidepoint(event.pos):
                    self._play_pop()
                    self.submenu = "levels"
                elif self.quit_rect.collidepoint(event.pos):
                    self._play_pop()
                    return 'quit'
            elif self.submenu == "levels":
                if self.lvl1_rect.collidepoint(event.pos):
                    self._play_pop()
                    return 'level_1'
                elif self.lvl2_rect.collidepoint(event.pos):
                    self._play_pop()
                    return 'level_2'
                elif self.back_rect.collidepoint(event.pos):
                    self._play_pop()
                    self.submenu = "main"
        return None

    def draw(self, screen):
        self.bg.draw(screen)
        # dark tint so UI stays readable over the scrolling background
        tint = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        tint.fill((0, 0, 0, 120))
        screen.blit(tint, (0, 0))
        screen.blit(self.title, self.title_rect)

        if self.submenu == "main":
            self._draw_image_btn(screen, self.start_btn, self.start_rect, self.start_hovered)
            self._draw_image_btn(screen, self.quit_btn, self.quit_rect, self.quit_hovered)
        elif self.submenu == "levels":
            self._draw_text_btn(screen, self.lvl1_rect, "Level 1", self.lvl1_hovered)
            self._draw_text_btn(screen, self.lvl2_rect, "Level 2", self.lvl2_hovered)
            self._draw_text_btn(screen, self.back_rect, "BACK", self.back_hovered)

    def _draw_image_btn(self, screen, img, rect, is_hovered):
        btn_img = img.copy()
        if is_hovered:
            btn_img.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(btn_img, rect)

    def _draw_text_btn(self, screen, rect, text, is_hovered):
        color = (100, 100, 150) if is_hovered else (70, 70, 100)
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 255), rect, 2, border_radius=10)  # Border
        txt_surf = self.font.render(text, True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=rect.center)
        screen.blit(txt_surf, txt_rect)