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
        # Initial image load with safety
        self.idle_path = Path("assets") / "Sprite" / "Idle" / "0_Forest_Ranger_Idle_000.png"
        self.animations = {}
        
        # Crop values
        self.w_bound, self.h_bound = 5, 15
        
        # Initial sprite setup
        temp_img = pygame.image.load(str(self.idle_path)).convert_alpha()
        self.image = self.image_transformer(str(self.idle_path), 0.1, self.w_bound, self.h_bound)
        self.rect = self.image.get_rect(midbottom=(x, y))
        
        # Hitbox setup - slightly smaller than image to prevent snagging
        self.hitbox = pygame.Rect(0, 0, 30, 60)
        self.hitbox.midbottom = self.rect.midbottom

        # Trailing
        self.trail_length = 8
        self.trail_pos = collections.deque(maxlen=self.trail_length)

        # Bulk Load Animations
        base_folder = Path("assets") / "Sprite"
        for folder in base_folder.iterdir():
            if folder.is_dir():
                folder_name = folder.name.lower()
                self.animations[folder_name] = []
                # Sort files to ensure animation sequence is correct
                for image_pth in sorted(folder.glob("*.png")):
                    img = self.image_transformer(str(image_pth), 0.1, self.w_bound, self.h_bound)
                    self.animations[folder_name].append(img)

        # Physics & States
        self.state = PlayerState.IDLE
        self.frame_count = 0.0
        self.pos = pygame.math.Vector2(self.hitbox.centerx, self.hitbox.bottom)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.facing = 1
        
        # Physics Constants
        self.speed = 1800.0
        self.max_walk = 450.0
        self.friction = -15.0
        self.gravity = 2600.0
        self.jump_strength = 900.0
        
        self.on_ground = False
        self.can_double_jump = True
        self.dashing = False
        self._dash_timer = 0.0
        self._dash_cd_timer = 0.0
        self.dash_speed = 1200.0
        self.dash_time = 0.2

        # Sounds (Wrapped in try/except to prevent exit if files are missing)
        try:
            self.jump_sound = pygame.mixer.Sound("assets/Sound/jump.mp3")
            self.dash_sound = pygame.mixer.Sound("assets/Sound/dash.mp3")
            self.run_sound = pygame.mixer.Sound("assets/Sound/run.mp3")
            self.run_sound_time = self.run_sound.get_length()
            self._run_sound_timer = 0.0
        except:
            self.jump_sound = self.dash_sound = self.run_sound = None
            print("Warning: Sound files missing.")

    def image_transformer(self, filepath, scale, w_bound, h_bound):
        image = pygame.image.load(filepath).convert_alpha()
        image = pygame.transform.scale_by(image, scale)
        width, height = image.get_size()
        # Clamp bounds to ensure subsurface is never outside the image
        rect = pygame.Rect(w_bound, h_bound, max(1, width - 2 * w_bound), max(1, height - 2 * h_bound))
        return image.subsurface(rect)

    def jump(self):
        if self.on_ground:
            self.vel.y = -self.jump_strength
            self.on_ground = False
            self.can_double_jump = True
            if self.jump_sound: self.jump_sound.play()
        elif self.can_double_jump:
            self.vel.y = -self.jump_strength * 0.85
            self.can_double_jump = False
            if self.jump_sound: self.jump_sound.play()

    def try_dash(self, dir_x):
        if self._dash_cd_timer <= 0 and not self.dashing:
            self.dashing = True
            self._dash_timer = self.dash_time
            self._dash_cd_timer = 0.8
            self.vel.x = dir_x * self.dash_speed
            if self.dash_sound: self.dash_sound.play()

    def update(self, dt, level):
        keys = pygame.key.get_pressed()
        self.acc.x = 0
        
        # Handle Horizontal Input
        if not self.dashing:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.acc.x = -self.speed
                self.facing = -1
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.acc.x = self.speed
                self.facing = 1
            else:
                # Stronger braking when no key is pressed
                self.vel.x *= 0.85

        # Physics Integration
        self.acc.y = self.gravity
        self.acc.x += self.vel.x * self.friction * 0.01
        
        if self.dashing:
            self._dash_timer -= dt
            if self._dash_timer <= 0:
                self.dashing = False
        else:
            self.vel.x += self.acc.x * dt
            # Clamp walking speed
            if abs(self.vel.x) > self.max_walk:
                self.vel.x = self.max_walk * (1 if self.vel.x > 0 else -1)

        self.vel.y += self.acc.y * dt

        # Collision X
        self.pos.x += self.vel.x * dt
        self.hitbox.centerx = round(self.pos.x)
        self._collide_axis(level.platforms, 'x')
        
        # Collision Y
        self.pos.y += self.vel.y * dt
        self.hitbox.bottom = round(self.pos.y)
        self._collide_axis(level.platforms, 'y')

        # Final visual placement
        self.rect.midbottom = self.hitbox.midbottom
        
        if self._dash_cd_timer > 0:
            self._dash_cd_timer -= dt

        self.update_state()
        self.update_animations(dt)

    def _collide_axis(self, platforms, axis):
        if axis == 'y': self.on_ground = False
        for p in platforms:
            if self.hitbox.colliderect(p):
                if axis == 'x':
                    if self.vel.x > 0: self.hitbox.right = p.left
                    elif self.vel.x < 0: self.hitbox.left = p.right
                    self.pos.x = self.hitbox.centerx
                    self.vel.x = 0
                elif axis == 'y':
                    if self.vel.y > 0:
                        self.hitbox.bottom = p.top
                        self.on_ground = True
                        self.can_double_jump = True
                        self.vel.y = 0
                    elif self.vel.y < 0:
                        self.hitbox.top = p.bottom
                        self.vel.y = 0
                    self.pos.y = self.hitbox.bottom

    def update_state(self):
        if not self.on_ground:
            self.state = PlayerState.JUMP if self.vel.y < 0 else PlayerState.FALL
        else:
            self.state = PlayerState.IDLE if abs(self.vel.x) < 50 else PlayerState.RUN

    def update_animations(self, dt):
        # Choose folder name
        anim_set = "dash" if self.dashing else self.state.name.lower()
        
        # SAFETY CHECK: If the folder doesn't exist, default to idle
        frames = self.animations.get(anim_set, self.animations.get("idle", []))
        
        if frames:
            self.frame_count += 12 * dt
            if self.frame_count >= len(frames):
                self.frame_count = 0
            
            raw_img = frames[int(self.frame_count)]
            if self.facing == -1:
                self.image = pygame.transform.flip(raw_img, True, False)
            else:
                self.image = raw_img
            
            # Re-sync rect to hitbox
            self.rect = self.image.get_rect(midbottom=self.hitbox.midbottom)

    def draw_trail(self, screen):
        # Only draw trail when dashing or moving very fast
        if self.dashing or abs(self.vel.x) > self.max_walk:
            self.trail_pos.append((self.rect.center, self.image.copy()))
        elif self.trail_pos:
            self.trail_pos.popleft()

        for i, (pos, img) in enumerate(self.trail_pos):
            alpha = int(128 * (i / len(self.trail_pos)))
            img.set_alpha(alpha)
            screen.blit(img, img.get_rect(center=pos))