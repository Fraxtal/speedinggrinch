import pygame
import collections

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player

class Effects():
	def __init__(self, player : 'Player'):
		self.player = player

		#trailing
		self.trail_length = 10
		self.trail_pos = collections.deque(maxlen=self.trail_length)

	def draw_trail(self, screen):
			self.trail_pos.append(self.player.rect.center)
			for i, pos in enumerate(self.trail_pos):
				ratio = int(125 * ((self.trail_length - i) / self.trail_length))
				trail_img = self.player.image.copy()

				color_mask = pygame.mask.from_surface(trail_img)
				color_mask = color_mask.to_surface(setcolor=(ratio, ratio, 255, 255), unsetcolor=(0, 0, 0, 0))

				trail_img.blit(color_mask, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
				trail_img.set_alpha(ratio)
				
				trail_rect = trail_img.get_rect(center=pos)
				screen.blit(trail_img, trail_rect)