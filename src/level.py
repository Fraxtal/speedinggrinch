import pygame
import os

class Level:
    def __init__(self, level_number):
        self.platforms = []
        self.level_number = level_number
        self.scroll = 0
        self.scroll_speed = 0.5 
        
        # Path logic based on your folder structure
        asset_folder = os.path.join("assets", "background")
        bg_file = "factorylevelone.png" if level_number == 1 else "factorylevelone.png"
        full_path = os.path.join(asset_folder, bg_file)

        try:
            self.bg_image = pygame.image.load(full_path).convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (1280, 720))
        except:
            print(f"FAILED TO LOAD BG: {full_path}")
            self.bg_image = pygame.Surface((1280, 720))
            self.bg_image.fill((30, 30, 80))

        self.bg_width = self.bg_image.get_width()
        self._create_layout()

    def _create_layout(self):
        W, H = 1280, 720
        if self.level_number == 1:
            self.platforms = [
                pygame.Rect(0, H - 40, W, 40),
                pygame.Rect(300, H - 160, 200, 24),
                pygame.Rect(700, H - 260, 220, 24)
            ]
        else:
            self.platforms = [pygame.Rect(0, H - 40, W, 40)]

    def update(self, player_vel_x, dt):
        self.scroll += player_vel_x * dt * self.scroll_speed

    def draw(self, surf):
        rel_x = int(self.scroll % self.bg_width)
        surf.blit(self.bg_image, (-rel_x, 0))
        surf.blit(self.bg_image, (-rel_x + self.bg_width, 0))
        surf.blit(self.bg_image, (-rel_x - self.bg_width, 0))

        for p in self.platforms:
            pygame.draw.rect(surf, (40, 40, 50), p)