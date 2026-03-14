import pygame
import os
from level import Level

DEFAULT_CONTROLS = {
    'left':  pygame.K_a,
    'right': pygame.K_d,
    'jump':  pygame.K_SPACE,
    'dash':  pygame.K_LSHIFT,
}

STORY_LINES = [
    "Santa's factory is not the cheerful place",
    "the world believes it to be.",
    "",
    "Every elf who works here signs a magical contract —",
    "one that binds them to the factory forever.",
    "",
    "Recently, elves have begun disappearing.",
    "Management claims they were reassigned,",
    "but no one has ever seen them again.",
    "",
    "You are a toy assembly elf who has decided",
    "to escape before you become the next missing worker.",
    "",
    "Tonight, while the machines run and supervisors",
    "patrol the halls, you must sneak through",
    "the factory unnoticed.",
    "",
    "Jump across obstacles. Avoid management.",
    "Do not get caught.",
    "",
    "Escape the factory.",
]

STORY_LINES_2 = [
    "You made it out of the factory.",
    "",
    "The cold air hits you like a wall of ice.",
    "For a moment, it feels like freedom.",
    "",
    "But the premises outside are no safe haven.",
    "Santa's patrol elves sweep the grounds,",
    "and the frozen terrain is full of its own dangers.",
    "",
    "You are not free yet.",
    "Not even close.",
    "",
    "Keep moving. The treeline is your only hope.",
    "Do not stop. Do not get caught.",
]


class MenuBackground:
    SCROLL_SPEED = 180
    FADE_DURATION = 1.2

    def __init__(self, screen_width, screen_height, level_number=1):
        self.W = screen_width
        self.H = screen_height
        self.level = Level(level_number)
        self.max_scroll = self.level.world_width - screen_width
        self.scroll = 0.0
        self._fade_alpha = 0
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


class StoryScroll:
    FADE_SPEED = 280

    def __init__(self, screen_width, screen_height, lines=None, bg_level=1):
        self.W = screen_width
        self.H = screen_height
        self.alpha = 0
        self.fading_in  = True
        self.fading_out = False
        self.done = False
        self._dismissed = False
        self.title_font = pygame.font.Font(None, 42)
        self.body_font  = pygame.font.Font(None, 30)
        self.hint_font  = pygame.font.Font(None, 24)
        _lines = lines if lines is not None else STORY_LINES
        self._title_surf = self.title_font.render("— BACKSTORY —", True, (255, 220, 120))
        self._line_surfs = [self.body_font.render(l, True, (220, 210, 190)) for l in _lines]
        self._hint_surf  = self.hint_font.render("Press any key or click to continue", True, (160, 150, 130))
        self._sfx = pygame.mixer.Sound(os.path.join("main_menu", "sfx", "pageflipsfx.mp3"))
        self._sfx.play()
        self.bg = MenuBackground(screen_width, screen_height, level_number=bg_level)
        self._pad = 48
        line_h = self.body_font.get_linesize()
        content_h = self.title_font.get_linesize() + 16 + len(_lines) * line_h + 24 + self.hint_font.get_linesize()
        panel_w = int(screen_width * 0.62)
        panel_h = min(content_h + self._pad * 2, screen_height - 80)
        self._panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
        self._panel_rect.center = (screen_width // 2, screen_height // 2)
        self._surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)

    def dismiss(self):
        if not self._dismissed and not self.fading_out:
            self._dismissed = True
            self.fading_in  = False
            self.fading_out = True
            self._sfx.play()

    def update(self, dt):
        step = self.FADE_SPEED * dt
        if self.fading_in:
            self.alpha = min(255, self.alpha + step)
            if self.alpha >= 255:
                self.fading_in = False
        elif self.fading_out:
            self.alpha = max(0, self.alpha - step)
            if self.alpha <= 0:
                self.done = True

    def draw(self, screen):
        a = int(self.alpha)
        pw, ph = self._panel_rect.size
        self._surf.fill((0, 0, 0, 0))
        pygame.draw.rect(self._surf, (30, 20, 10, 210), (0, 0, pw, ph), border_radius=12)
        pygame.draw.rect(self._surf, (180, 140, 80, 180), (0, 0, pw, ph), 2, border_radius=12)
        tx = (pw - self._title_surf.get_width()) // 2
        self._surf.blit(self._title_surf, (tx, self._pad))
        line_h = self.body_font.get_linesize()
        y = self._pad + self.title_font.get_linesize() + 16
        for surf in self._line_surfs:
            lx = (pw - surf.get_width()) // 2
            self._surf.blit(surf, (lx, y))
            y += line_h
        hx = (pw - self._hint_surf.get_width()) // 2
        self._surf.blit(self._hint_surf, (hx, ph - self._pad))
        self._surf.set_alpha(a)
        screen.blit(self._surf, self._panel_rect)


class MainMenu:
    def __init__(self, screen_width, screen_height, both_complete=False):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.both_complete = both_complete
        self.submenu = "main"
        self.bg = MenuBackground(screen_width, screen_height)
        asset_path = 'main_menu'
        try:
            self.title        = pygame.image.load(os.path.join(asset_path, 'menu_title.png')).convert_alpha()
            self.start_btn    = pygame.image.load(os.path.join(asset_path, 'button_start.png')).convert_alpha()
            self.settings_btn = pygame.image.load(os.path.join(asset_path, 'button_settings.png')).convert_alpha()
            self.quit_btn     = pygame.image.load(os.path.join(asset_path, 'button_quit.png')).convert_alpha()
            btn_w = int(screen_width * 0.25)
            btn_h = int(screen_height * 0.125)
            self.start_btn    = pygame.transform.scale(self.start_btn,    (btn_w, btn_h))
            self.settings_btn = pygame.transform.scale(self.settings_btn, (btn_w, btn_h))
            self.quit_btn     = pygame.transform.scale(self.quit_btn,     (btn_w, btn_h))
        except Exception:
            self.title = pygame.Surface((400, 100), pygame.SRCALPHA)
            self.start_btn = pygame.Surface((200, 50)); self.start_btn.fill((100, 100, 100))
            self.settings_btn = pygame.Surface((200, 50)); self.settings_btn.fill((80, 80, 120))
            self.quit_btn = pygame.Surface((200, 50)); self.quit_btn.fill((100, 100, 100))
        self.title_rect    = self.title.get_rect(center=(screen_width // 2, screen_height // 3))
        self.start_rect    = self.start_btn.get_rect(center=(screen_width // 2, screen_height // 2 + 30))
        self.settings_rect = self.settings_btn.get_rect(center=(screen_width // 2, screen_height // 2 + 140))
        self.quit_rect     = self.quit_btn.get_rect(center=(screen_width // 2, screen_height // 2 + 250))
        self.font = pygame.font.Font(None, 50)
        self.lvl1_rect = pygame.Rect(0, 0, 250, 60)
        self.lvl2_rect = pygame.Rect(0, 0, 250, 60)
        self.back_rect = pygame.Rect(0, 0, 250, 60)
        self.lvl1_rect.center = (screen_width // 2, screen_height // 2 - 20)
        self.lvl2_rect.center = (screen_width // 2, screen_height // 2 + 60)
        self.back_rect.center = (screen_width // 2, screen_height // 2 + 180)
        self.start_hovered = self.settings_hovered = self.quit_hovered = False
        self.lvl1_hovered  = self.lvl2_hovered = self.back_hovered = False
        self._prev_hovered = set()
        self.pop_sfx = pygame.mixer.Sound(os.path.join(asset_path, 'sfx', 'popsfx.mp3'))
        self._sfx_channel = pygame.mixer.find_channel()

    def _play_pop(self):
        if self._sfx_channel and not self._sfx_channel.get_busy():
            self._sfx_channel.play(self.pop_sfx)

    def update(self, mouse_pos, dt=0):
        self.bg.update(dt)
        self.start_hovered    = self.start_rect.collidepoint(mouse_pos)
        self.settings_hovered = self.settings_rect.collidepoint(mouse_pos)
        self.quit_hovered     = self.quit_rect.collidepoint(mouse_pos)
        self.lvl1_hovered     = self.lvl1_rect.collidepoint(mouse_pos)
        self.lvl2_hovered     = self.lvl2_rect.collidepoint(mouse_pos)
        self.back_hovered     = self.back_rect.collidepoint(mouse_pos)
        now_hovered = {k for k, v in {
            'start': self.start_hovered, 'settings': self.settings_hovered,
            'quit': self.quit_hovered, 'lvl1': self.lvl1_hovered,
            'lvl2': self.lvl2_hovered, 'back': self.back_hovered,
        }.items() if v}
        if now_hovered - self._prev_hovered:
            self._play_pop()
        self._prev_hovered = now_hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.submenu == "main":
                if self.start_rect.collidepoint(event.pos):
                    self._play_pop()
                    return 'levels' if self.both_complete else 'level_1'
                elif self.settings_rect.collidepoint(event.pos):
                    self._play_pop()
                    return 'settings'
                elif self.quit_rect.collidepoint(event.pos):
                    self._play_pop()
                    return 'quit'
            elif self.submenu == "levels":
                if self.lvl1_rect.collidepoint(event.pos):
                    self._play_pop(); return 'level_1'
                elif self.lvl2_rect.collidepoint(event.pos):
                    self._play_pop(); return 'level_2'
                elif self.back_rect.collidepoint(event.pos):
                    self._play_pop(); self.submenu = "main"
        return None

    def draw(self, screen):
        self.bg.draw(screen)
        tint = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        tint.fill((0, 0, 0, 120))
        screen.blit(tint, (0, 0))
        screen.blit(self.title, self.title_rect)
        if self.submenu == "main":
            self._draw_image_btn(screen, self.start_btn,    self.start_rect,    self.start_hovered)
            self._draw_image_btn(screen, self.settings_btn, self.settings_rect, self.settings_hovered)
            self._draw_image_btn(screen, self.quit_btn,     self.quit_rect,     self.quit_hovered)
        elif self.submenu == "levels":
            self._draw_text_btn(screen, self.lvl1_rect, "Level 1", self.lvl1_hovered)
            self._draw_text_btn(screen, self.lvl2_rect, "Level 2", self.lvl2_hovered)
            self._draw_text_btn(screen, self.back_rect, "BACK",    self.back_hovered)

    def _draw_image_btn(self, screen, img, rect, is_hovered):
        btn_img = img.copy()
        if is_hovered:
            btn_img.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(btn_img, rect)

    def _draw_text_btn(self, screen, rect, text, is_hovered):
        color = (100, 100, 150) if is_hovered else (70, 70, 100)
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 255), rect, 2, border_radius=10)
        txt_surf = self.font.render(text, True, (255, 255, 255))
        screen.blit(txt_surf, txt_surf.get_rect(center=rect.center))


class PauseMenu:
    _ITEMS = ['Resume', 'Settings', 'Quit to Menu']

    def __init__(self, screen_width, screen_height):
        self.W = screen_width
        self.H = screen_height
        self._font_title = pygame.font.Font(None, 72)
        self._font_item  = pygame.font.Font(None, 46)
        self._hovered    = None
        panel_w, panel_h = 360, 310
        self._panel = pygame.Rect(0, 0, panel_w, panel_h)
        self._panel.center = (screen_width // 2, screen_height // 2)
        start_y = self._panel.y + 105
        self._rects = [
            pygame.Rect(self._panel.x + 30, start_y + i * 58, panel_w - 60, 44)
            for i in range(len(self._ITEMS))
        ]

    def handle_event(self, event):
        """Returns 'resume', 'settings', or 'quit_to_menu', else None."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'resume'
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self._rects):
                if rect.collidepoint(event.pos):
                    return ['resume', 'settings', 'quit_to_menu'][i]
        return None

    def update(self, mouse_pos):
        self._hovered = next(
            (i for i, r in enumerate(self._rects) if r.collidepoint(mouse_pos)), None
        )

    def draw(self, screen, frozen_frame):
        screen.blit(frozen_frame, (0, 0))
        tint = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        tint.fill((0, 0, 0, 160))
        screen.blit(tint, (0, 0))
        panel_surf = pygame.Surface(self._panel.size, pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (20, 18, 30, 220), panel_surf.get_rect(), border_radius=14)
        pygame.draw.rect(panel_surf, (140, 120, 200, 180), panel_surf.get_rect(), 2, border_radius=14)
        screen.blit(panel_surf, self._panel)
        title = self._font_title.render("PAUSED", True, (220, 210, 255))
        screen.blit(title, title.get_rect(centerx=self._panel.centerx, top=self._panel.y + 18))
        for i, (rect, label) in enumerate(zip(self._rects, self._ITEMS)):
            hovered = self._hovered == i
            pygame.draw.rect(screen, (100, 80, 160) if hovered else (55, 50, 80), rect, border_radius=8)
            pygame.draw.rect(screen, (200, 180, 255) if hovered else (140, 120, 200), rect, 2, border_radius=8)
            lbl = self._font_item.render(label, True, (255, 255, 255))
            screen.blit(lbl, lbl.get_rect(center=rect.center))


class SettingsScreen:
    PANEL_W  = 700
    PANEL_H  = 520
    SLIDER_W = 200
    SLIDER_H = 8
    THUMB_R  = 10
    ROW_H    = 54

    _ACTION_LABELS = [
        ('left',  'Move Left'),
        ('right', 'Move Right'),
        ('jump',  'Jump'),
        ('dash',  'Dash'),
    ]

    def __init__(self, screen_width, screen_height, controls, music_volume, return_to='menu'):
        self.W = screen_width
        self.H = screen_height
        self.controls    = dict(controls)
        self.music_volume = music_volume
        self.return_to   = return_to   # 'menu' or 'paused'

        self._font_title = pygame.font.Font(None, 52)
        self._font_label = pygame.font.Font(None, 34)
        self._font_hint  = pygame.font.Font(None, 26)

        self._panel = pygame.Rect(0, 0, self.PANEL_W, self.PANEL_H)
        self._panel.center = (screen_width // 2, screen_height // 2)

        slider_x = self._panel.x + 280
        vol_y    = self._panel.y + 90
        self._slider_track    = pygame.Rect(slider_x, vol_y, self.SLIDER_W, self.SLIDER_H)
        self._dragging_slider = False

        self._rebinding  = None
        bind_start_y = self._panel.y + 170
        self._bind_rects = {
            action: pygame.Rect(slider_x, bind_start_y + i * self.ROW_H, 180, 38)
            for i, (action, _) in enumerate(self._ACTION_LABELS)
        }

        self._back_rect = pygame.Rect(0, 0, 160, 44)
        self._back_rect.bottomright = (self._panel.right - 20, self._panel.bottom - 16)
        self._back_hovered = False

        self._surf = pygame.Surface((self.PANEL_W, self.PANEL_H), pygame.SRCALPHA)

    def _thumb_x(self):
        return int(self._slider_track.x + self.music_volume * self.SLIDER_W)

    def _key_name(self, key):
        name = pygame.key.name(key)
        return name.upper() if len(name) == 1 else name.title()

    def handle_event(self, event):
        """Returns 'back' when done, else None."""
        if self._rebinding:
            if event.type == pygame.KEYDOWN:
                if event.key != pygame.K_ESCAPE:
                    self.controls[self._rebinding] = event.key
                self._rebinding = None
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            thumb_rect = pygame.Rect(
                self._thumb_x() - self.THUMB_R,
                self._slider_track.centery - self.THUMB_R,
                self.THUMB_R * 2, self.THUMB_R * 2
            )
            if thumb_rect.collidepoint(mx, my) or self._slider_track.collidepoint(mx, my):
                self._dragging_slider = True
                self._update_volume(mx)
            for action, rect in self._bind_rects.items():
                if rect.collidepoint(mx, my):
                    self._rebinding = action
                    return None
            if self._back_rect.collidepoint(mx, my):
                return 'back'

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging_slider = False

        if event.type == pygame.MOUSEMOTION and self._dragging_slider:
            self._update_volume(event.pos[0])

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'back'

        return None

    def _update_volume(self, mouse_x):
        rel = mouse_x - self._slider_track.x
        self.music_volume = max(0.0, min(1.0, rel / self.SLIDER_W))
        pygame.mixer.music.set_volume(self.music_volume)

    def update(self, mouse_pos):
        self._back_hovered = self._back_rect.collidepoint(mouse_pos)

    def draw(self, screen, bg_or_frozen):
        # bg_or_frozen: a MenuBackground (menu settings) or a Surface (pause settings)
        if isinstance(bg_or_frozen, pygame.Surface):
            screen.blit(bg_or_frozen, (0, 0))
        else:
            bg_or_frozen.draw(screen)
        tint = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        tint.fill((0, 0, 0, 150))
        screen.blit(tint, (0, 0))

        self._surf.fill((0, 0, 0, 0))
        pygame.draw.rect(self._surf, (20, 18, 30, 220), (0, 0, self.PANEL_W, self.PANEL_H), border_radius=14)
        pygame.draw.rect(self._surf, (140, 120, 200, 180), (0, 0, self.PANEL_W, self.PANEL_H), 2, border_radius=14)
        screen.blit(self._surf, self._panel)

        px, py = self._panel.x, self._panel.y
        title = self._font_title.render("SETTINGS", True, (220, 210, 255))
        screen.blit(title, title.get_rect(centerx=self._panel.centerx, top=py + 22))

        vol_label = self._font_label.render("Music Volume", True, (200, 195, 220))
        screen.blit(vol_label, (px + 40, self._slider_track.y - 4))
        pygame.draw.rect(screen, (60, 55, 80), self._slider_track, border_radius=4)
        filled = pygame.Rect(self._slider_track.x, self._slider_track.y,
                             int(self.music_volume * self.SLIDER_W), self.SLIDER_H)
        pygame.draw.rect(screen, (160, 130, 255), filled, border_radius=4)
        thumb_x = self._thumb_x()
        pygame.draw.circle(screen, (220, 200, 255), (thumb_x, self._slider_track.centery), self.THUMB_R)
        pygame.draw.circle(screen, (255, 255, 255), (thumb_x, self._slider_track.centery), self.THUMB_R, 2)
        pct = self._font_hint.render(f"{int(self.music_volume * 100)}%", True, (180, 175, 200))
        screen.blit(pct, (self._slider_track.right + 12, self._slider_track.y - 4))

        bind_title = self._font_label.render("Keybinds", True, (200, 195, 220))
        screen.blit(bind_title, (px + 40, py + 140))

        for action, label in self._ACTION_LABELS:
            rect = self._bind_rects[action]
            lbl = self._font_label.render(label, True, (210, 205, 230))
            screen.blit(lbl, (px + 40, rect.y + 6))
            waiting = self._rebinding == action
            pygame.draw.rect(screen, (100, 60, 160) if waiting else (55, 50, 80), rect, border_radius=8)
            pygame.draw.rect(screen, (255, 220, 80) if waiting else (140, 120, 200), rect, 2, border_radius=8)
            kt = self._font_hint.render("Press key..." if waiting else self._key_name(self.controls[action]),
                                        True, (255, 255, 255))
            screen.blit(kt, kt.get_rect(center=rect.center))

        bc = (90, 80, 130) if self._back_hovered else (55, 50, 80)
        pygame.draw.rect(screen, bc, self._back_rect, border_radius=8)
        pygame.draw.rect(screen, (140, 120, 200), self._back_rect, 2, border_radius=8)
        back_lbl = self._font_label.render("Back", True, (255, 255, 255))
        screen.blit(back_lbl, back_lbl.get_rect(center=self._back_rect.center))

        if self._rebinding:
            hint = self._font_hint.render("Press any key to rebind  •  ESC to cancel", True, (255, 220, 80))
            screen.blit(hint, hint.get_rect(centerx=self._panel.centerx, bottom=self._panel.bottom - 60))
