import pygame
import os
import random
import math

class Level:
    SPIKE_SIZE = 14
    def __init__(self, level_number):

        self.platforms = []
        self.spike_rects = []
        self.machine_rects = []
        self.enemies = []
        self.goal_rect = None
        self.goal_timer = 0.0
        self.level_number = level_number

        # camera scroll position
        self.scroll = 0
        self.scroll_y = 0

        # screen size
        self.screen_width = 1280
        self.screen_height = 720

        if level_number == 1:
            self.world_width = 6000
            self.world_height = self.screen_height
            asset_folder = os.path.join("assets", "background")
            full_path = os.path.join(asset_folder, "factorylevelone.png")
            try:
                self.bg_image = pygame.image.load(full_path).convert()
                self.bg_image = pygame.transform.scale(self.bg_image, (1280, 720))
            except Exception:
                print(f"FAILED TO LOAD BG: {full_path}")
                self.bg_image = pygame.Surface((1280, 720))
                self.bg_image.fill((30, 30, 80))
            self._load_tiles()
        else:
            self.world_width = self.screen_width
            self.world_height = 4000
            self.bg_image = self._make_level2_background()

        self.bg_width = self.bg_image.get_width()
        self._create_layout()

    def _load_tiles(self):
        T = 32
        ts = pygame.image.load(os.path.join("assets", "tiles", "Tileset.png")).convert_alpha()
        def t(col, row): return ts.subsurface((col * T, row * T, T, T))
        # Row 4: top surface  — left-cap, mid, right-cap
        # Row 5: body         — left-cap, mid, right-cap
        # Row 6: bottom       — left-cap, mid, right-cap
        self._tiles = {
            "top_l":  t(0, 4), "top_m":  t(1, 4), "top_r":  t(2, 4),
            "body_l": t(0, 5), "body_m": t(1, 5), "body_r": t(2, 5),
            "bot_l":  t(0, 6), "bot_m":  t(1, 6), "bot_r":  t(2, 6),
        }

    def _make_level2_background(self):
        surf = pygame.Surface((self.screen_width, self.screen_height))
        surf.fill((10, 8, 25))
        rng = random.Random(42)
        for _ in range(220):
            x = rng.randint(0, self.screen_width - 1)
            y = rng.randint(0, self.screen_height - 1)
            r = rng.choice([1, 1, 1, 2])
            brightness = rng.randint(160, 255)
            pygame.draw.circle(surf, (brightness, brightness, brightness), (x, y), r)

        def draw_ridge(y_base, color, segments, roughness):
            pts = [(0, self.screen_height)]
            x, y = 0, y_base
            step = self.screen_width // segments
            for _ in range(segments + 1):
                y += rng.randint(-roughness, roughness)
                y = max(y_base - roughness * 3, min(y_base + roughness, y))
                pts.append((x, y))
                x += step
            pts.append((self.screen_width, self.screen_height))
            pygame.draw.polygon(surf, color, pts)

        draw_ridge(self.screen_height - 200, (20, 18, 45), 12, 40)
        draw_ridge(self.screen_height - 130, (30, 26, 60), 18, 25)
        draw_ridge(self.screen_height - 70,  (38, 32, 72), 24, 15)
        return surf

    def _create_layout(self):
        if self.level_number == 1:
            self._create_layout_1()
        else:
            self._create_layout_2()

    def _create_layout_1(self):
        T = 32
        H = self.screen_height
        ground_y = H - T * 3
        self.platforms = [pygame.Rect(0, ground_y, self.world_width, T * 3)]

        wall_defs = [
            (700,   5),
            (1500,  7),
            (2400,  6),
            (3300,  7),
            (4200,  5),
            (5100,  6),
        ]
        for wx, wh in wall_defs:
            self.platforms.append(pygame.Rect(wx, ground_y - wh * T, T * 2, wh * T))

        plat_defs = [
            (400,   H - T*8,   4),
            (768,   H - T*12,  4),   # over wall 1
            (1100,  H - T*8,   4),
            (1568,  H - T*14,  4),   # over wall 2
            (1900,  H - T*9,   4),
            (2468,  H - T*13,  4),   # over wall 3
            (2800,  H - T*8,   4),
            (3368,  H - T*14,  4),   # over wall 4
            (3700,  H - T*9,   4),
            (4268,  H - T*11,  4),   # over wall 5
            (4600,  H - T*8,   4),
            (5168,  H - T*13,  4),   # over wall 6
            (5568,  H - T*9,   5),   # near goal
        ]
        for x, y, tw in plat_defs:
            self.platforms.append(pygame.Rect(x, y, tw * T, T * 2))

        # Machines on floating platforms
        rng = random.Random(99)
        MW, MH = 36, 48
        num_walls = len(wall_defs)
        for plat in self.platforms[num_walls + 3:]:  # skip ground, walls, first 2 floaters
            if plat.width < MW * 2:
                continue
            if rng.random() < 0.30:
                mx = rng.randint(plat.x + 8, plat.x + plat.width - MW - 8)
                self.machine_rects.append(pygame.Rect(mx, plat.y - MH, MW, MH))

        # Ground enemies between walls
        erng = random.Random(77)
        wall_xs = [wx for wx, _ in wall_defs]
        segments = list(zip([0] + wall_xs, wall_xs + [self.world_width - 200]))
        for seg_start, seg_end in segments[1:]:
            seg_w = seg_end - seg_start - T * 2
            if seg_w < 80:
                continue
            if erng.random() < 0.5:
                patrol = pygame.Rect(seg_start + T * 2, ground_y, seg_w, T * 3)
                ex = erng.randint(patrol.x, patrol.right - 28)
                self.enemies.append((ex, patrol))

        # Floating platform enemies
        for plat in self.platforms[num_walls + 4:]:
            if plat.width < 120:
                continue
            if erng.random() < 0.25:
                ex = erng.randint(plat.x + 10, plat.x + plat.width - 38)
                self.enemies.append((ex, plat))

    def _create_layout_2(self):
        W = self.screen_width
        H = self.world_height
        S = self.SPIKE_SIZE

        self.platforms = [pygame.Rect(0, H - 40, W, 40)]

        rng = random.Random(7)
        columns = [W // 4, W // 2, 3 * W // 4]
        plat_w = 180

        y = H - 160
        i = 0
        while y > 120:
            col = columns[i % len(columns)]
            x = col - plat_w // 2 + rng.randint(-40, 40)
            x = max(20, min(W - plat_w - 20, x))
            self.platforms.append(pygame.Rect(x, y, plat_w, 24))

            if i > 3 and rng.random() < 0.30:
                spike_x = x + rng.randint(10, plat_w - 50)
                count = rng.randint(2, 4)
                for k in range(count):
                    self.spike_rects.append(pygame.Rect(spike_x + k * S, y - S, S, S))

            progress = 1 - (y / H)
            y -= int(110 + 35 * progress + progress * 40)
            i += 1

        self.goal_rect = pygame.Rect(W // 2 - 40, 30, 80, 100)

    def update(self, player, dt=0):
        if self.level_number == 1:
            target_scroll = player.rect.centerx - self.screen_width // 2
            target_scroll = max(0, min(target_scroll, self.world_width - self.screen_width))
            speed_factor = min(abs(player.vel.x) / 600, 1)
            self.scroll += (target_scroll - self.scroll) * (0.15 + 0.35 * speed_factor)
        else:
            target_y = player.hitbox.centery - self.screen_height // 2
            target_y = max(0, min(target_y, self.world_height - self.screen_height))
            self.scroll_y += (target_y - self.scroll_y) * 0.12
            self.scroll = 0
            if self.goal_rect:
                self.goal_timer += dt if dt > 0 else 1 / 60

    def draw_bg_at(self, surf, scroll):
        """Draw level 1 background + platforms at an arbitrary scroll (used by menu)."""
        saved = self.scroll
        self.scroll = scroll
        self._draw_level1(surf)
        self.scroll = saved

    def draw(self, surf):
        if self.level_number == 1:
            self._draw_level1(surf)
        else:
            self._draw_level2(surf)

    def _draw_level1(self, surf):
        rel_x = int(self.scroll) % self.bg_width
        surf.blit(self.bg_image, (-rel_x, 0))
        surf.blit(self.bg_image, (-rel_x + self.bg_width, 0))
        surf.blit(self.bg_image, (-rel_x - self.bg_width, 0))
        for p in self.platforms:
            self._draw_tiled_platform(surf, p)
        for m in self.machine_rects:
            sx = m.x - int(self.scroll)
            # body
            pygame.draw.rect(surf, (80, 60, 60), (sx, m.y, m.width, m.height), border_radius=4)
            pygame.draw.rect(surf, (200, 80, 40), (sx, m.y, m.width, m.height), 2, border_radius=4)
            # spinning blade indicator (two crossed lines)
            cx, cy = sx + m.width // 2, m.y + m.height // 2
            pygame.draw.line(surf, (255, 120, 40), (cx - 10, cy - 10), (cx + 10, cy + 10), 3)
            pygame.draw.line(surf, (255, 120, 40), (cx + 10, cy - 10), (cx - 10, cy + 10), 3)

    def _draw_tiled_platform(self, surf, p):
        T = 32
        tl = self._tiles
        sx = p.x - int(self.scroll)
        cols = max(1, p.width // T)
        rows = max(1, p.height // T)
        for r in range(rows):
            for c in range(cols):
                if r == 0:
                    row_key = "top"
                elif r == rows - 1:
                    row_key = "bot"
                else:
                    row_key = "body"
                if cols == 1:
                    col_key = "m"
                elif c == 0:
                    col_key = "l"
                elif c == cols - 1:
                    col_key = "r"
                else:
                    col_key = "m"
                tile = tl[f"{row_key}_{col_key}"]
                surf.blit(tile, (sx + c * T, p.y + r * T))

    def _draw_level2(self, surf):
        bg_h = self.bg_image.get_height()
        sy = int(self.scroll_y)
        rel_y = sy % bg_h
        for tile_y in (-rel_y - bg_h, -rel_y, -rel_y + bg_h, -rel_y + bg_h * 2):
            surf.blit(self.bg_image, (0, tile_y))

        for p in self.platforms:
            dr = pygame.Rect(p.x, p.y - sy, p.width, p.height)
            pygame.draw.rect(surf, (55, 48, 90), dr)
            pygame.draw.line(surf, (110, 90, 160), dr.topleft, dr.topright, 2)

        S = self.SPIKE_SIZE
        for r in self.spike_rects:
            dx, dy = r.x, r.y - sy
            pygame.draw.polygon(surf, (220, 60, 60), [
                (dx + S // 2, dy), (dx, dy + S), (dx + S, dy + S)
            ])

        if self.goal_rect:
            pulse = 0.5 + 0.5 * math.sin(self.goal_timer * 3)
            dr = pygame.Rect(self.goal_rect.x, self.goal_rect.y - sy, self.goal_rect.width, self.goal_rect.height)
            for i in range(4, 0, -1):
                glow = pygame.Surface((dr.width + i * 12, dr.height + i * 12), pygame.SRCALPHA)
                glow.fill((100, 255, 200, int(40 * pulse * i)))
                surf.blit(glow, (dr.x - i * 6, dr.y - i * 6))
            core = pygame.Surface((dr.width, dr.height), pygame.SRCALPHA)
            core.fill((140, 255, 210, 180))
            surf.blit(core, dr)
            pygame.draw.rect(surf, (200, 255, 230), dr, 3)
            font = pygame.font.Font(None, 28)
            lbl = font.render("GOAL", True, (255, 255, 255))
            surf.blit(lbl, lbl.get_rect(centerx=dr.centerx, top=dr.top + 6))

    def check_machine_collision(self, hitbox):
        return any(hitbox.colliderect(m) for m in self.machine_rects)

    def check_spike_collision(self, hitbox):
        return any(hitbox.colliderect(r) for r in self.spike_rects)

    def check_goal_collision(self, hitbox):
        if self.goal_rect:
            return self.goal_rect.colliderect(hitbox)
        return False