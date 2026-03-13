import pygame
from pathlib import Path
from enum import Enum, auto
import collections

class PlayerState(Enum):
    IDLE = auto()
    RUN = auto()
    JUMP = auto()
    FALL = auto()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets\\Sprite\\Idle\\0_Forest_Ranger_Idle_000.png").convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 0.1)
        w_bound = 5
        h_bound = 15
        width, height = self.image.get_size()
        self.image = self.image.subsurface(pygame.Rect(w_bound, h_bound, width - 2*w_bound, height - 2*h_bound))
        self.rect = self.image.get_rect(midbottom=(x, y))

        self.hitbox = pygame.Rect(0, 0, 30, 60)
        self.hitbox.midbottom = self.rect.midbottom
        
        # debugging overlay
        self.hitbox_overlay = pygame.Surface(self.hitbox.size, pygame.SRCALPHA)
        self.hitbox_overlay.fill((255, 125, 125, 150))
        self.debug_font = pygame.font.Font(None, 20)
        self.debug_text = self.debug_font.render("", True, (255, 125, 125))
        self.debug_text_rect = self.debug_text.get_rect()
        self.debug_text_rect.midbottom = self.hitbox.midright
        self.debug_info_cooldown = 0.5
        self._debug_info_cooldown_timer = 0.0

        #trailing
        self.trail_length = 8
        self.trail_pos = collections.deque(maxlen=self.trail_length)

        # animation frames
        self.animations = {}
        self.state = PlayerState.IDLE
        base_folder = Path("assets")
        for image_pth in base_folder.rglob("*.png"):
            folder_name = image_pth.parent.name
            folder_name = folder_name.lower()
            if folder_name not in self.animations:
                self.animations[folder_name] = []
            img = self.image_transformer(str(image_pth), 0.1, w_bound, h_bound)
            self.animations[folder_name].append(img)
        self.frame_count = 0

        #positions
        self.pos = pygame.math.Vector2(self.hitbox.centerx, self.hitbox.bottom)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)

        self.facing = 1
        self.speed = 1200.0  # acceleration
        self.max_walk = 340.0
        self.friction = -12.0
        self.gravity = 2400.0

        # jump
        self.jump_sound = pygame.mixer.Sound("assets\\Sound\\jump.mp3")
        self.jump_strength = 820.0
        self.on_ground = False
        self.can_double_jump = True

        # dash
        self.dash_sound = pygame.mixer.Sound("assets\\Sound\\dash.mp3")
        self.dash_speed = 700.0
        self.dash_time = 0.3
        self.dash_cooldown = 0.7
        self._dash_timer = 0.0
        self._dash_cd_timer = 0.0
        self.dashing = False

        # hurt
        self.hurt_sound = pygame.mixer.Sound("assets\\Sound\\hurt.mp3")
        self.hurt_time = 0.5
        self.hurt_cooldown = 0.8
        self._hurt_timer = 0.0
        self._hurt_cd_timer = 0.0
        self.hurting = False

        # run
        self.run_sound = pygame.mixer.Sound("assets\\Sound\\run.mp3")
        self.run_sound_time = self.run_sound.get_length()
        self._run_sound_timer = 0.0

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
            self.jump_sound.play()
        elif self.can_double_jump:
            self.vel.y = -self.jump_strength * 0.9
            self.can_double_jump = False
            self.state = PlayerState.JUMP
            self.jump_sound.play()

    def try_dash(self, dir_x):
        if self._dash_cd_timer <= 0 and not self.dashing:
            self.dashing = True
            self._dash_timer = self.dash_time
            self._dash_cd_timer = self.dash_cooldown
            self.dash_sound.play()
            self.vel.x = dir_x * self.dash_speed

    def hurt(self, dir_x):
        if self._hurt_cd_timer <= 0 and not self.hurting:
            self.hurting = True
            self._hurt_timer = self.hurt_time
            self._hurt_cd_timer = self.hurt_cooldown
            self.hurt_sound.play()
            self.facing = abs(dir_x) / dir_x

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

        if self.hurting:
            self._hurt_timer -= dt
            if self._hurt_timer <= 0:
                self.hurting = False
            else:
                self.vel.x = self.facing * 2

        self.vel.y += self.acc.y * dt

        # simple Euler position update
        self.pos.x += self.vel.x * dt
        self.hitbox.centerx = int(self.pos.x)
        self._collide_axis(level.platforms, 'x')

        self.pos.y += self.vel.y * dt
        self.hitbox.bottom = int(self.pos.y)
        self._collide_axis(level.platforms, 'y')

        if self._dash_cd_timer > 0:
            self._dash_cd_timer -= dt

        # constant deceleration
        self.vel.x += (0 - self.vel.x)/20

        # update state and animation
        self.update_state()
        self.update_animations()
        self.frame_count += 0.5

        # handle running sound
        if self.state == PlayerState.RUN:
            if self._run_sound_timer > 0:
                self._run_sound_timer -= dt
            else:
                self.run_sound.play()
                self._run_sound_timer = self.run_sound_time
        else:
            self.run_sound.stop()
            self._run_sound_timer = 0

    # update the state of player
    def update_state(self):
        if self.on_ground:
            self.state = PlayerState.IDLE if abs(self.vel.x) <= 30 else PlayerState.RUN
            return
        if self.vel.y > 0:
            self.state = PlayerState.FALL
            return

    # update the animation of player according to state
    def update_animations(self):
        if self.dashing:
            animations = self.animations["dash"]
        elif self.hurting:
            animations = self.animations["hurt"]
        else:
            animations = self.animations[self.state.name.lower()]
        animation_length = len(animations)

        if (self.frame_count >= animation_length):
            self.frame_count = 0
        self.image = animations[int(self.frame_count)] if self.facing == 1 else pygame.transform.flip(animations[int(self.frame_count)], True, False)
        self.rect = self.image.get_rect(midbottom=self.hitbox.midbottom)

    # helper method to bulk processing images
    def image_transformer(self, filepath, scale, w_bound, h_bound):
        image = pygame.image.load(filepath).convert_alpha()
        image = pygame.transform.scale_by(image, scale)
        width, height = image.get_size()
        image = image.subsurface(pygame.Rect(w_bound, h_bound, width - 2*w_bound, height - 2*h_bound))
        return image

    # drawing trailing effects
    def draw_trail(self, screen, camera_scroll):
        self.trail_pos.append(self.rect.center)
        self.trail_length = 12 if self.dashing else 8
        if len(self.trail_pos) != self.trail_length:
            self.trail_pos = collections.deque(self.trail_pos, maxlen=self.trail_length)
        for i, pos in enumerate(self.trail_pos):
            ratio = int(125 * ((self.trail_length - i) / self.trail_length))
            trail_img = self.image.copy()

            color_mask = pygame.mask.from_surface(trail_img)
            color_mask = color_mask.to_surface(setcolor=(ratio, ratio, 255, 255), unsetcolor=(0, 0, 0, 0))

            trail_img.blit(color_mask, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            trail_img.set_alpha(ratio/2)

            trail_rect = trail_img.get_rect(center=(pos[0] - camera_scroll, pos[1]))
            screen.blit(trail_img, trail_rect)

    # draw debug info

    def draw_debug(self, dt, screen):
        if self._debug_info_cooldown_timer <= 0:
            self._debug_info_cooldown_timer = self.debug_info_cooldown
            self.debug_text = self.debug_font.render(f"x-Vel: {round(self.vel.x, 2)}  y-Vel: {round(self.vel.y, 2)}", True, (255, 125, 125))
        else:
            self._debug_info_cooldown_timer -= dt

        self.debug_text_rect.midbottom = self.hitbox.midright
        screen.blit(self.hitbox_overlay, self.hitbox)
        screen.blit(self.debug_text, self.debug_text_rect)

    def _collide_axis(self, platforms, axis):
        for p in platforms:
            if self.hitbox.colliderect(p):
                if axis == 'x':
                    if self.vel.x > 0:
                        self.hitbox.right = p.left
                    elif self.vel.x < 0:
                        self.hitbox.left = p.right
                    self.pos.x = self.hitbox.centerx
                    self.vel.x = 0
                elif axis == 'y':
                    if self.vel.y > 0:
                        self.hitbox.bottom = p.top
                        self.on_ground = True
                        self.can_double_jump = True
                    elif self.vel.y < 0:
                        self.hitbox.top = p.bottom
                    self.pos.y = self.hitbox.bottom
                    self.vel.y = 0