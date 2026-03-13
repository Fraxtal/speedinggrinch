import pygame

class Level:
    def __init__(self):
        # Simple platform layout as rects
        self.platforms = []
        self._create_demo_level()

    def _create_demo_level(self):
        W, H = 1280, 720
        floor = pygame.Rect(0, H - 40, W, 40)
        self.platforms.append(floor)

        # Some floating platforms
        self.platforms.append(pygame.Rect(300, H - 160, 200, 24))
        self.platforms.append(pygame.Rect(700, H - 260, 220, 24))
        self.platforms.append(pygame.Rect(1050, H - 360, 180, 24))

    def draw(self, surf):
        for p in self.platforms:
            pygame.draw.rect(surf, (80, 80, 80), p)