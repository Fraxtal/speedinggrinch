import pygame
from pathlib import Path
from enum import Enum, auto
import collections
from menu import DEFAULT_CONTROLS

class PlayerState(Enum):
    IDLE = auto()
    RUN = auto()
    JUMP = auto()
    FALL = auto()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets\\sprites\\idle\\0_Forest_Ranger_Idle_000.png").convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 0.1)
        w_bound = 5
        h_bound = 15
        width, height = self.image.get_size()
        self.image = self.image.subsurface(pygame.Rect(w_bound, h_bound, width - 2*w_bound, height - 2*h_bound))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.hitbox = pygame.Rect(0, 0, 30, 60)
        self.hitbox.midbottom = self.rect.midbottom
        self._normal_hitbox_width = 30
        self._dash_hitbox_width = 16
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
        base_folder = Path("assets") / "sprites"
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
        self.jump_sound = pygame.mixer.Sound("assets\\audio\\jump.mp3")
        self.jump_strength = 820.0
        self.on_ground = False
        self.can_double_jump = True
        # dash
        self.dash_sound = pygame.mixer.Sound("assets\\audio\\dash.mp3")
        self.dash_speed = 700.0
        self.dash_time = 0.3
        self.dash_cooldown = 0.7
        self._dash_timer = 0.0
        self._dash_cd_timer = 0.0
        self.dashing = False
        # stamina bar
        self.stamina_rect = pygame.Rect(90, 55, 380, 10)
        # health bar
        self.max_hp = 100
        self.hp = 100
        self.prev_hp = 100
        self.temp_hp = 100
        self.health_max_width = 380
        self.health_rect = pygame.Rect(90, 30, 380, 15)
        # status
        self.status_overlay = pygame.Surface((480, 70), pygame.SRCALPHA)
        self.status_overlay.fill((0, 0, 0, 120))
        self.status_rect = self.status_overlay.get_rect()
        self.status_rect.topleft = (10, 10)
        self.status_font = pygame.font.Font(None, 20)
        self.hp_text = self.status_font.render("HP: ", True, (255, 255, 255))
        self.hp_text_rect = self.hp_text.get_rect()
        self.hp_text_rect.topleft = (self.health_rect.x - 70, self.health_rect.y - 2)
        self.stamina_text = self.status_font.render("Stamina: ", True, (255, 255, 255))
        self.stamina_text_rect = self.hp_text.get_rect()
        self.stamina_text_rect.topleft = (self.stamina_rect.x - 70, self.stamina_rect.y - 2)
        # hurt
        self.hp = 100
        self.hurt_sound = pygame.mixer.Sound("assets\\audio\\hurt.mp3")
        self.hurt_time = 0.5
        self.hurt_cooldown = 0.8
        self._hurt_timer = 0.0
        self._hurt_cd_timer = 0.0
        self.hurting = False
        # run
        self.run_sound = pygame.mixer.Sound("assets\\audio\\run.mp3")
        self.run_sound_time = self.run_sound.get_length()
        self._run_sound_timer = 0.0

    def handle_input(self, keys, controls):
        self.acc.x = 0
        if keys[controls['left']]:
            self.acc.x = -self.speed
            self.facing = -1
        if keys[controls['right']]:
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

    def try_hurt(self, dir_x):
        if self._hurt_cd_timer <= 0 and not self.hurting:
            self.hurting = True
            self.hp -= 10
            self._hurt_timer = self.hurt_time
            self._hurt_cd_timer = self.hurt_cooldown
            self.hurt_sound.play()
            self.facing = abs(dir_x) / dir_x

    def update(self, dt, level, controls=None):
        keys = pygame.key.get_pressed()
        self.handle_input(keys, controls or DEFAULT_CONTROLS)
        # apply horizontal acceleration and friction
        self.acc.y = self.gravity
        self.acc.x += self.vel.x * self.friction * 0.001
        # integrate
        if self.dashing:
            self._dash_timer -= dt
            self.hitbox.width = self._dash_hitbox_width
            if self._dash_timer <= 0:
                self.dashing = False
                self.hitbox.width = self._normal_hitbox_width
        else:
            self.vel.x += self.acc.x * dt
            # clamp
            if abs(self.vel.x) > self.max_walk:
                self.vel.x = self.max_walk * (1 if self.vel.x > 0 else -1)
        if self.hurting:
            self._hurt_timer -= dt
            if self._hurt_timer <= 0:
                self.hurting = False
            elif not self.dashing:
                self.vel.x = self.facing * -50
                if self.frame_count % 3 == 0:
                    self.image.fill((150, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
        # update temp hp for animation
        if self.temp_hp > self.hp:
            self.temp_hp -= 1.5
            if self.temp_hp < self.hp:
                self.temp_hp = self.hp
        self.vel.y += self.acc.y * dt
        # simple Euler position update
        self.pos.x += self.vel.x * dt
        self.hitbox.centerx = int(self.pos.x)
        self._collide_axis(level.platforms, 'x')
        # clamp to world bounds
        if self.hitbox.left < 0:
            self.hitbox.left = 0
            self.pos.x = self.hitbox.centerx
            self.vel.x = 0
        if self.hitbox.right > level.world_width:
            self.hitbox.right = level.world_width
            self.pos.x = self.hitbox.centerx
            self.vel.x = 0
        self.pos.y += self.vel.y * dt
        self.hitbox.bottom = int(self.pos.y)
        self._collide_axis(level.platforms, 'y')
        if self._dash_cd_timer > 0:
            self._dash_cd_timer -= dt
        if self._hurt_cd_timer > 0:
            self._hurt_cd_timer -= dt
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
    def draw_trail(self, screen, camera_scroll, camera_scroll_y=0):
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
            trail_rect = trail_img.get_rect(center=(pos[0] - camera_scroll, pos[1] - camera_scroll_y))
            screen.blit(trail_img, trail_rect)
            
    def draw_status_bar(self, screen):
        # background
        screen.blit(self.status_overlay, self.status_rect)
        # caption
        screen.blit(self.hp_text, self.hp_text_rect)
        screen.blit(self.stamina_text, self.stamina_text_rect)
        # temp hp bar (for smooth view)
        if self.temp_hp > self.hp:
            temp_hp_length = self.temp_hp / self.max_hp * self.health_max_width
            temp_hp_rect = pygame.Rect(self.health_rect.x,
                                    self.health_rect.y,
                                    temp_hp_length,
                                    self.health_rect.height)
            pygame.draw.rect(screen, (255, 200, 0, 255), temp_hp_rect)
        # hp bar
        if (self.hp != self.prev_hp):
            ratio = self.hp / self.max_hp
            self.health_rect = pygame.Rect(self.health_rect.x, 
                                    self.health_rect.y, 
                                    self.health_max_width * ratio, 
                                    self.health_rect.height)
            self.prev_hp = self.hp
        pygame.draw.rect(screen, (255, 125, 125, 255), self.health_rect)
        # stamina bar (dash cd)
        if (self._dash_cd_timer > 0):
            ratio = (self.dash_cooldown - self._dash_cd_timer) / self.dash_cooldown
            cd_progress = int(ratio * 255)
            color = ((255 - cd_progress), cd_progress, 0, 255)
            cur_rect = pygame.Rect(self.stamina_rect.x, self.stamina_rect.y, self.stamina_rect.width * ratio, self.stamina_rect.height)
            pygame.draw.rect(screen, color, cur_rect)
        else:
            pygame.draw.rect(screen, (0, 255, 0, 255), self.stamina_rect)
            pass

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