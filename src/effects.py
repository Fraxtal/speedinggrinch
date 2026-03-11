import pygame
import collections
import player

class Effects():
	#trailing
	trail_length = 10
	trail_pos = collections.deque(maxlen=trail_length)

	def draw_tail(player, screen):
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

