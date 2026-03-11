import pygame
import collections

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((36, 64), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (200, 40, 40), (0, 0, 36, 64))
        self.rect = self.image.get_rect(topleft=(x, y))

        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)

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

        #trailing
        self.trail_length = 10
        self.trail_pos = collections.deque(maxlen=self.trail_length)

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
        elif self.can_double_jump:
            self.vel.y = -self.jump_strength * 0.9
            self.can_double_jump = False

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

    #trailing
    def draw_trail(player, screen):
                player.trail_pos.append(player.rect.center)
                for i, pos in enumerate(player.trail_pos):
                    ratio = int(255 * (i / player.trail_length))
                    trail_img = player.image.copy()
                    color_mask = pygame.Surface(trail_img.get_size(), pygame.SRCALPHA)
                    color_mask.fill((ratio, ratio, 255, 255))
                    trail_img.blit(color_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    trail_img.set_alpha(ratio)
                    
                    trail_rect = trail_img.get_rect(center=pos)
                    screen.blit(trail_img, trail_rect)

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
