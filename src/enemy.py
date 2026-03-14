import pygame
import math
from pathlib import Path


def _load_animations(scale=0.1, w_bound=5, h_bound=15):
    animations = {}
    base_folder = Path("assets") / "Sprite"
    for image_pth in sorted(base_folder.rglob("*.png")):
        folder_name = image_pth.parent.name.lower()
        if folder_name not in animations:
            animations[folder_name] = []
        img = pygame.image.load(str(image_pth)).convert_alpha()
        img = pygame.transform.scale_by(img, scale)
        w, h = img.get_size()
        img = img.subsurface(pygame.Rect(w_bound, h_bound, w - 2 * w_bound, h - 2 * h_bound))
        # tint red to distinguish from player
        tint = pygame.Surface(img.get_size(), pygame.SRCALPHA)
        tint.fill((100, 0, 0, 40))
        img = img.copy()
        img.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        animations[folder_name].append(img)
    return animations


_SHARED_ANIMATIONS = None


def get_animations():
    global _SHARED_ANIMATIONS
    if _SHARED_ANIMATIONS is None:
        _SHARED_ANIMATIONS = _load_animations()
    return _SHARED_ANIMATIONS


class Enemy:
    WIDTH, HEIGHT = 28, 48
    SPEED = 80
    DETECT_RANGE = 140
    DETECT_ANGLE = 35

    def __init__(self, x, platform):
        self.platform = platform
        self.animations = get_animations()
        self.frame = 0.0
        self.facing = 1
        self.vel_x = self.SPEED

        first = self.animations["idle"][0]
        self.rect = first.get_rect()
        self.rect.midbottom = (x + self.WIDTH // 2, platform.y)

    def update(self, dt):
        self.rect.x += int(self.vel_x * dt)
        if self.rect.right >= self.platform.right:
            self.rect.right = self.platform.right
            self.vel_x = -self.SPEED
            self.facing = -1
        elif self.rect.left <= self.platform.left:
            self.rect.left = self.platform.left
            self.vel_x = self.SPEED
            self.facing = 1
        self.frame = (self.frame + 0.4) % len(self.animations["run"])

    def can_see(self, player_hitbox):
        ex = self.rect.centerx + self.facing * self.WIDTH // 2
        ey = self.rect.centery
        px, py = player_hitbox.centerx, player_hitbox.centery
        dx, dy = px - ex, py - ey
        dist = math.hypot(dx, dy)
        if dist == 0 or dist > self.DETECT_RANGE:
            return False
        dot = (dx / dist) * self.facing
        return math.degrees(math.acos(max(-1.0, min(1.0, dot)))) <= self.DETECT_ANGLE

    def draw(self, surf, scroll):
        frame_img = self.animations["run"][int(self.frame)]
        if self.facing == -1:
            frame_img = pygame.transform.flip(frame_img, True, False)
        draw_rect = frame_img.get_rect(midbottom=(self.rect.centerx - int(scroll), self.rect.bottom))
        surf.blit(frame_img, draw_rect)

        # detection cone
        ex = self.rect.centerx - int(scroll) + self.facing * self.WIDTH // 2
        ey = self.rect.centery
        half_rad = math.radians(self.DETECT_ANGLE)
        base_angle = 0.0 if self.facing == 1 else math.pi
        pts = [(ex, ey)]
        for i in range(9):
            a = base_angle - half_rad + (2 * half_rad * i / 8)
            pts.append((ex + math.cos(a) * self.DETECT_RANGE,
                        ey + math.sin(a) * self.DETECT_RANGE))
        pygame.draw.polygon(surf, (255, 60, 60, 40), pts)
