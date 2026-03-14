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
        self.scroll = 0
        self.screen_width = 1280
        self.screen_height = 720
        self.snowflakes = []
        if level_number == 1:
            self.world_width = 7000
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
        else:
            self.world_width = 8000
            self.world_height = self.screen_height
            asset_folder = os.path.join("assets", "background")
            full_path = os.path.join(asset_folder, "factoryleveltwo.png")
            try:
                self.bg_image = pygame.image.load(full_path).convert()
                self.bg_image = pygame.transform.scale(self.bg_image, (1280, 720))
            except Exception:
                print(f"FAILED TO LOAD BG: {full_path}")
                self.bg_image = pygame.Surface((1280, 720))
                self.bg_image.fill((30, 30, 80))
            rng = random.Random()
            self.snowflakes = [
                [rng.randint(0, self.screen_width),
                 rng.randint(0, self.screen_height),
                 rng.uniform(40, 110),
                 rng.choice([1, 1, 2, 2, 3])]
                for _ in range(160)
            ]
        self._load_tiles()
        self.gift_img = pygame.image.load(os.path.join("assets", "background", "giftobstacle.png")).convert_alpha()
        self.gift_img = pygame.transform.scale(self.gift_img, (36, 48))
        self.bg_width = self.bg_image.get_width()
        self._create_layout()
    def _load_tiles(self):
        T = 32
        ts = pygame.image.load(os.path.join("assets", "tiles", "Tileset.png")).convert_alpha()
        def t(col, row):
            return ts.subsurface((col * T, row * T, T, T))
        self._tiles = {
            "top_l":  t(0, 4), "top_m":  t(1, 4), "top_r":  t(2, 4),
            "body_l": t(0, 5), "body_m": t(1, 5), "body_r": t(2, 5),
            "bot_l":  t(0, 6), "bot_m":  t(1, 6), "bot_r":  t(2, 6),
        }
        ts2 = pygame.image.load(os.path.join("assets", "tiles", "Tileset 2.png")).convert_alpha()
        def t2(col, row):
            return ts2.subsurface((col * T, row * T, T, T))
        self._snow_tiles = {
            "top_l":  t2(0, 0), "top_m":  t2(1, 0), "top_r":  t2(2, 0),
            "body_l": t2(0, 1), "body_m": t2(1, 1), "body_r": t2(2, 1),
            "bot_l":  t2(0, 2), "bot_m":  t2(1, 2), "bot_r":  t2(2, 2),
        }

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
            (700, 5),
            (1500, 7),
            (2400, 6),
            (3300, 7),
            (4200, 5),
            (5100, 6),
        ]
        for wx, wh in wall_defs:
            self.platforms.append(pygame.Rect(wx, ground_y - wh * T, T * 2, wh * T))
        plat_defs = [
            (400,  H - T*8,  4),
            (768,  H - T*12, 4),
            (1100, H - T*8,  4),
            (1568, H - T*14, 4),
            (1900, H - T*9,  4),
            (2468, H - T*13, 4),
            (2800, H - T*8,  4),
            (3368, H - T*14, 4),
            (3700, H - T*9,  4),
            (4268, H - T*11, 4),
            (4600, H - T*8,  4),
            (5168, H - T*13, 4),
            (5568, H - T*9,  5),
            (6000, H - T*11, 4),
            (6500, H - T*8,  4),
            (7000, H - T*12, 4),
        ]
        for x, y, tw in plat_defs:
            self.platforms.append(pygame.Rect(x, y, tw * T, T * 2))
        self.platforms[-1].width = self.world_width - self.platforms[-1].x
        rng = random.Random(99)
        MW, MH = 36, 48
        num_walls = len(wall_defs)
        for plat in self.platforms[num_walls + 3:]:
            if plat.width < MW * 2:
                continue
            if rng.random() < 0.30:
                mx = rng.randint(plat.x + 8, plat.x + plat.width - MW - 8)
                self.machine_rects.append(pygame.Rect(mx, plat.y - MH, MW, MH))
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
        for plat in self.platforms[num_walls + 4:]:
            if plat.width < 120:
                continue
            if erng.random() < 0.25:
                ex = erng.randint(plat.x + 10, plat.x + plat.width - 38)
                self.enemies.append((ex, plat))
        self.goal_rect = pygame.Rect(self.world_width - 160, ground_y - T * 5, 80, T * 5)
    
    def _create_layout_2(self):
        T = 32
        H = self.screen_height
        S = self.SPIKE_SIZE
        ground_y = H - T * 3
        self.platforms = [pygame.Rect(0, ground_y, self.world_width, T * 3)]
        wall_defs = [
            (800, 5),
            (1700, 4),
            (2600, 7),
            (3700, 5),
            (4800, 6),
            (6000, 4),
            (7200, 6),
        ]
        for wx, wh in wall_defs:
            self.platforms.append(pygame.Rect(wx, ground_y - wh * T, T * 2, wh * T))
        plat_defs = [
            (450,  H - T * 10, 5),
            (1100, H - T * 7,  4),
            (1750, H - T * 13, 5),
            (2300, H - T * 8,  4),
            (2650, H - T * 11, 5),
            (3200, H - T * 6,  4),
            (3750, H - T * 14, 4),
            (4300, H - T * 9,  5),
            (4850, H - T * 7,  4),
            (5400, H - T * 12, 5),
            (6050, H - T * 8,  4),
            (6600, H - T * 11, 5),
            (7250, H - T * 9,  4),
        ]
        for x, y, tw in plat_defs:
            self.platforms.append(pygame.Rect(x, y, tw * T, T * 2))
        rng = random.Random(13)
        num_walls = len(wall_defs)
        floating_start = 1 + num_walls
        for plat in self.platforms[floating_start + 2:]:
            if rng.random() < 0.35:
                count = rng.randint(2, 4)
                max_offset = plat.width - count * S - 8
                if max_offset < 8:
                    continue
                sx = plat.x + rng.randint(8, max_offset)
                for k in range(count):
                    self.spike_rects.append(pygame.Rect(sx + k * S, plat.y - S, S, S))
        grng = random.Random(88)
        MW, MH = 36, 48
        for plat in self.platforms[floating_start:]:
            if plat.width < MW * 2:
                continue
            if grng.random() < 0.45:
                mx = grng.randint(plat.x + 8, plat.x + plat.width - MW - 8)
                self.machine_rects.append(pygame.Rect(mx, plat.y - MH, MW, MH))
        erng = random.Random(61)
        wall_xs = [wx for wx, _ in wall_defs]
        segments = list(zip([0] + wall_xs, wall_xs + [self.world_width - 200]))
        for seg_start, seg_end in segments[1:]:
            seg_w = seg_end - seg_start - T * 2
            if seg_w < 80:
                continue
            if erng.random() < 0.70:
                patrol = pygame.Rect(seg_start + T * 2, ground_y, seg_w, T * 3)
                ex = erng.randint(patrol.x, patrol.right - 28)
                self.enemies.append((ex, patrol))
        for plat in self.platforms[floating_start + 2:]:
            if plat.width < 120:
                continue
            if erng.random() < 0.40:
                ex = erng.randint(plat.x + 10, plat.x + plat.width - 38)
                self.enemies.append((ex, plat))
        self.goal_rect = pygame.Rect(self.world_width - 160, ground_y - T * 5, 80, T * 5)

    def update(self, player, dt=0):
        target_scroll = player.rect.centerx - self.screen_width // 2
        target_scroll = max(0, min(target_scroll, self.world_width - self.screen_width))
        speed_factor = min(abs(player.vel.x) / 600, 1)
        self.scroll += (target_scroll - self.scroll) * (0.15 + 0.35 * speed_factor)
        if self.goal_rect:
            self.goal_timer += dt if dt > 0 else 1 / 60
        for flake in self.snowflakes:
            flake[1] += flake[2] * dt
            flake[0] += flake[2] * 0.18 * dt  # gentle horizontal drift
            if flake[1] > self.screen_height:
                flake[1] = -flake[3] * 2
                flake[0] = random.randint(0, self.screen_width)

    def draw_bg_at(self, surf, scroll):
        saved = self.scroll
        self.scroll = scroll
        self._draw_level(surf)
        self.scroll = saved

    def draw(self, surf):
        self._draw_level(surf)

    def _draw_level(self, surf):
        rel_x = int(self.scroll) % self.bg_width
        surf.blit(self.bg_image, (-rel_x, 0))
        surf.blit(self.bg_image, (-rel_x + self.bg_width, 0))
        surf.blit(self.bg_image, (-rel_x - self.bg_width, 0))
        for flake in self.snowflakes:
            alpha = max(60, int(200 * (flake[3] / 3)))
            flake_surf = pygame.Surface((flake[3] * 2, flake[3] * 2), pygame.SRCALPHA)
            pygame.draw.circle(flake_surf, (255, 255, 255, alpha), (flake[3], flake[3]), flake[3])
            surf.blit(flake_surf, (int(flake[0]) - flake[3], int(flake[1]) - flake[3]))
        for p in self.platforms:
            self._draw_tiled_platform(surf, p)
        S = self.SPIKE_SIZE
        for r in self.spike_rects:
            dx = r.x - int(self.scroll)
            dy = r.y
            pygame.draw.polygon(surf, (100, 180, 255), [(dx + S // 2, dy), (dx, dy + S), (dx + S, dy + S)])
        for m in self.machine_rects:
            surf.blit(self.gift_img, (m.x - int(self.scroll), m.y))
        if self.goal_rect:
            pulse = 0.5 + 0.5 * math.sin(self.goal_timer * 3)
            dr = pygame.Rect(self.goal_rect.x - int(self.scroll), self.goal_rect.y, self.goal_rect.width, self.goal_rect.height)
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

    def _draw_snow_platform(self, surf, p):
        sx = p.x - int(self.scroll)
        SNOW_H = 8
        GRASS_H = 6
        grass_rect = pygame.Rect(sx, p.y, p.width, p.height)
        pygame.draw.rect(surf, (55, 100, 45), grass_rect)
        pygame.draw.rect(surf, (70, 130, 55), pygame.Rect(sx, p.y, p.width, GRASS_H))
        pygame.draw.rect(surf, (230, 240, 250), pygame.Rect(sx, p.y, p.width, SNOW_H))
        pygame.draw.line(surf, (255, 255, 255), (sx, p.y), (sx + p.width, p.y), 2)
        pygame.draw.line(surf, (45, 85, 38), (sx, p.y + SNOW_H), (sx, p.y + p.height), 1)
        pygame.draw.line(surf, (45, 85, 38), (sx + p.width - 1, p.y + SNOW_H), (sx + p.width - 1, p.y + p.height), 1)

    def _draw_tiled_platform(self, surf, p):
        T = 32
        if self.level_number == 2:
            tl = self._snow_tiles
        else:
            tl = self._tiles
        sx = p.x - int(self.scroll)
        cols = max(1, math.ceil(p.width / T))
        rows = max(1, math.ceil(p.height / T))
        for r in range(rows):
            for c in range(cols):
                row_key = "top" if r == 0 else ("bot" if r == rows - 1 else "body")
                col_key = "m" if cols == 1 else ("l" if c == 0 else ("r" if c == cols - 1 else "m"))
                surf.blit(tl[f"{row_key}_{col_key}"], (sx + c * T, p.y + r * T))

    def check_machine_collision(self, hitbox):
        return any(hitbox.colliderect(m) for m in self.machine_rects)

    def check_spike_collision(self, hitbox):
        return any(hitbox.colliderect(r) for r in self.spike_rects)

    def check_goal_collision(self, hitbox):
        if self.goal_rect:
            return self.goal_rect.colliderect(hitbox)
        return False