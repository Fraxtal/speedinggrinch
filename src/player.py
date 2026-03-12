import pygame
import collections
from pathlib import Path
from effects import Effects
from enum import Enum, auto

class PlayerState(Enum):
    IDLE = auto()
    RUN = auto()
    JUMP = auto()
    FALL = auto()
    HURT = auto()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("asset\\Sprite\\Idle\\0_Forest_Ranger_Idle_000.png").convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 0.1)
        bound = 15
        width, height = self.image.get_size()
        self.image = self.image.subsurface(pygame.Rect(bound, bound, width - 2*bound, height - 2*bound))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.effect = Effects(self)

        # animations
        self.animations = {}
        self.state = PlayerState.IDLE
        base_folder = Path("asset")
        for image_pth in base_folder.rglob("*.png"):
            folder_name = image_pth.parent.name
            if folder_name not in self.animations:
                self.animations[folder_name] = []
            img = self.image_tranformer(str(image_pth), 0.1, bound)
            self.animations[folder_name].append(img)
        self.frame_count = 0

        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)

        self.facing = 1
        self.speed = 1600.0  # acceleration
        self.max_walk = 420.0
        self.friction = -12.0
        self.gravity = 2400.0
        self.jump_strength = 820.0

        self.on_ground = False
        self.can_double_jump = True

        # dash
        self.dash_speed = 900.0
        self.dash_time = 0.12
        self.dash_cooldown = 0.7
        self._dash_timer = 0.0
        self._dash_cd_timer = 0.0
        self.dashing = False

    def handle_input(self, keys):
        self.acc.x = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.acc.x = -self.speed
            self.facing = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.acc.x = self.speed
            self.facing = 1

    def jump(self):
        if self.on_ground:
            self.vel.y = -self.jump_strength
            self.on_ground = False
            self.can_double_jump = True
            self.state = PlayerState.JUMP
        elif self.can_double_jump:
            self.vel.y = -self.jump_strength * 0.9
            self.can_double_jump = False
            self.state = PlayerState.JUMP

    def try_dash(self, dir_x):
        if self._dash_cd_timer <= 0 and not self.dashing:
            self.dashing = True
            self._dash_timer = self.dash_time
            self._dash_cd_timer = self.dash_cooldown
            self.vel.x = dir_x * self.dash_speed

    def update(self, dt, level):
        keys = pygame.key.get_pressed()
        self.handle_input(keys)

        # apply horizontal acceleration and friction
        self.acc.y = self.gravity
        self.acc.x += self.vel.x * self.friction * 0.001

        # integrate
        if self.dashing:
            self._dash_timer -= dt
            if self._dash_timer <= 0:
                self.dashing = False
        else:
            self.vel.x += self.acc.x * dt
            # clamp
            if abs(self.vel.x) > self.max_walk:
                self.vel.x = self.max_walk * (1 if self.vel.x > 0 else -1)

        self.vel.y += self.acc.y * dt

        # simple Euler position update
        self.pos.x += self.vel.x * dt
        self.rect.x = int(self.pos.x)
        self._collide_axis(level.platforms, 'x')

        self.pos.y += self.vel.y * dt
        self.rect.y = int(self.pos.y)
        self._collide_axis(level.platforms, 'y')

        if self._dash_cd_timer > 0:
            self._dash_cd_timer -= dt

        # constant deceleration
        self.vel.x += (0 - self.vel.x)/20

        # update state and animation
        self.update_state()
        self.update_animations()
        self.frame_count += 0.5

    def update_state(self):
        if self.on_ground:
            self.state = PlayerState.IDLE if abs(self.vel.x) <= 20 else PlayerState.RUN
            return
        if self.vel.y > 0:
            self.state = PlayerState.FALL
            return

    def update_animations(self):
        if self.dashing:
            animations = self.animations["dash"]
        else:
            animations = self.animations[self.state.name.lower()]
        animation_length = len(animations)
        if (self.frame_count >= animation_length):
            self.frame_count = 0
        self.image = animations[int(self.frame_count)] if self.facing == 1 else pygame.transform.flip(animations[int(self.frame_count)], True, False)
        old_rect = self.rect
        self.rect = self.image.get_rect(topleft=old_rect.topleft)

    def image_tranformer(self, filepath, scale, bound):
        image = pygame.image.load(filepath).convert_alpha()
        image = pygame.transform.scale_by(image, scale)
        width, height = image.get_size()
        image = image.subsurface(pygame.Rect(bound, bound, width - 2*bound, height - 2*bound))
        return image

    def draw_effects(self, screen):
        self.effect.draw_trail(screen)

    def _collide_axis(self, platforms, axis):
        for p in platforms:
            if self.rect.colliderect(p):
                if axis == 'x':
                    if self.vel.x > 0:
                        self.rect.right = p.left
                    elif self.vel.x < 0:
                        self.rect.left = p.right
                    self.pos.x = self.rect.x
                    self.vel.x = 0
                elif axis == 'y':
                    if self.vel.y > 0:
                        self.rect.bottom = p.top
                        self.on_ground = True
                        self.can_double_jump = True
                    elif self.vel.y < 0:
                        self.rect.top = p.bottom
                    self.pos.y = self.rect.y
                    self.vel.y = 0
