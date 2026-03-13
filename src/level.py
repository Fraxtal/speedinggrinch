import pygame
import os
import random

class Level:
    def __init__(self, level_number):

        self.platforms = []
        self.level_number = level_number

        # camera scroll position
        self.scroll = 0

        # screen size
        self.screen_width = 1280
        self.screen_height = 720

        # level size
        self.world_width = 6000

        asset_folder = os.path.join("assets", "background")
        bg_file = "factorylevelone.png" if level_number == 1 else "factorylevelone.jpg"
        full_path = os.path.join(asset_folder, bg_file)

        try:
            self.bg_image = pygame.image.load(full_path).convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (1280, 720))
        except:
            print(f"FAILED TO LOAD BG: {full_path}")
            self.bg_image = pygame.Surface((1280, 720))
            self.bg_image.fill((30,30,80))

        self.bg_width = self.bg_image.get_width()

        self._create_layout()

    def _create_layout(self):

        H = self.screen_height

        # ground
        self.platforms = [
            pygame.Rect(0, H-40, self.world_width, 40)
        ]

        # platforms
        self.platforms.extend([
            pygame.Rect(300, H-160, 200, 24),
            pygame.Rect(700, H-260, 220, 24),
            pygame.Rect(1200, H-200, 200, 24),
            pygame.Rect(1700, H-300, 200, 24),
            pygame.Rect(2200, H-220, 200, 24),
            pygame.Rect(2700, H-350, 200, 24),
            pygame.Rect(3200, H-180, 200, 24),
            pygame.Rect(3700, H-260, 200, 24),
            pygame.Rect(4200, H-320, 200, 24),
            pygame.Rect(4700, H-200, 200, 24),
            pygame.Rect(5200, H-260, 200, 24)
        ])

        # random extra platforms
        for i in range(8):
            x = 800 + i*500
            y = random.randint(250,600)
            self.platforms.append(pygame.Rect(x,y,180,24))

    # CAMERA FOLLOW PLAYER
    def update(self, player):

        target_scroll = player.rect.centerx - self.screen_width // 2

    # keep camera inside level bounds
        if target_scroll < 0:
            target_scroll = 0
        if target_scroll > self.world_width - self.screen_width:
            target_scroll = self.world_width - self.screen_width

    # camera speed based on player velocity
        speed_factor = min(abs(player.vel.x) / 600, 1)

        camera_speed = 0.15 + (0.35 * speed_factor)

        self.scroll += (target_scroll - self.scroll) * camera_speed

    def draw(self, surf):

        # background scroll
        rel_x = self.scroll % self.bg_width

        surf.blit(self.bg_image, (-rel_x,0))
        surf.blit(self.bg_image, (-rel_x + self.bg_width,0))
        surf.blit(self.bg_image, (-rel_x - self.bg_width,0))

        # draw platforms
        for p in self.platforms:

            draw_rect = pygame.Rect(
                p.x - self.scroll,
                p.y,
                p.width,
                p.height
            )

            pygame.draw.rect(surf,(40,40,50),draw_rect)