import pygame
import os

class MainMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.submenu = "main"  # Initial menu state
        
        # Load assets (Keeping your original asset loading logic)
        asset_path = 'main_menu'
        try:
            self.title = pygame.image.load(os.path.join(asset_path, 'menu_title.png')).convert_alpha()
            self.start_btn = pygame.image.load(os.path.join(asset_path, 'button_start.png')).convert_alpha()
            self.quit_btn = pygame.image.load(os.path.join(asset_path, 'button_quit.png')).convert_alpha()
            
            # Scale buttons
            self.start_btn = pygame.transform.scale(self.start_btn, (int(self.screen_width * 0.25), int(self.screen_height * 0.125)))
            self.quit_btn = pygame.transform.scale(self.quit_btn, (int(self.screen_width * 0.25), int(self.screen_height * 0.125)))
        except:
            # Fallback if your specific button images aren't in the folder
            self.title = pygame.Surface((400, 100), pygame.SRCALPHA)
            self.start_btn = pygame.Surface((200, 50))
            self.start_btn.fill((100, 100, 100))
            self.quit_btn = pygame.Surface((200, 50))
            self.quit_btn.fill((100, 100, 100))

        # Position elements (Main Menu)
        self.title_rect = self.title.get_rect(center=(screen_width // 2, screen_height // 3))
        self.start_rect = self.start_btn.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
        self.quit_rect = self.quit_btn.get_rect(center=(screen_width // 2, screen_height // 2 + 170))
        
        # Level Selection Rects (We use text for levels, or you can use images)
        self.font = pygame.font.Font(None, 50)
        self.lvl1_rect = pygame.Rect(0, 0, 250, 60)
        self.lvl2_rect = pygame.Rect(0, 0, 250, 60)
        self.back_rect = pygame.Rect(0, 0, 250, 60)
        
        self.lvl1_rect.center = (screen_width // 2, screen_height // 2 - 20)
        self.lvl2_rect.center = (screen_width // 2, screen_height // 2 + 60)
        self.back_rect.center = (screen_width // 2, screen_height // 2 + 180)
        
        # Hover states
        self.start_hovered = False
        self.quit_hovered = False
        self.lvl1_hovered = False
        self.lvl2_hovered = False
        self.back_hovered = False
    
    def update(self, mouse_pos):
        # Reset all hovers
        self.start_hovered = self.start_rect.collidepoint(mouse_pos)
        self.quit_hovered = self.quit_rect.collidepoint(mouse_pos)
        self.lvl1_hovered = self.lvl1_rect.collidepoint(mouse_pos)
        self.lvl2_hovered = self.lvl2_rect.collidepoint(mouse_pos)
        self.back_hovered = self.back_rect.collidepoint(mouse_pos)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.submenu == "main":
                if self.start_rect.collidepoint(event.pos):
                    self.submenu = "levels"  # Change to level selection
                elif self.quit_rect.collidepoint(event.pos):
                    return 'quit'
            elif self.submenu == "levels":
                if self.lvl1_rect.collidepoint(event.pos):
                    return 'level_1'
                elif self.lvl2_rect.collidepoint(event.pos):
                    return 'level_2'
                elif self.back_rect.collidepoint(event.pos):
                    self.submenu = "main" # Go back to title
        return None
    
    def draw(self, screen):
        # Keeping your original dark blue background color
        screen.fill((50, 50, 80))
        
        # Always draw title
        screen.blit(self.title, self.title_rect)
        
        if self.submenu == "main":
            # Draw Main Menu buttons with hover
            self._draw_image_btn(screen, self.start_btn, self.start_rect, self.start_hovered)
            self._draw_image_btn(screen, self.quit_btn, self.quit_rect, self.quit_hovered)
        
        elif self.submenu == "levels":
            # Draw Level Selection buttons
            self._draw_text_btn(screen, self.lvl1_rect, "Level 1", self.lvl1_hovered)
            self._draw_text_btn(screen, self.lvl2_rect, "Level 2", self.lvl2_hovered)
            self._draw_text_btn(screen, self.back_rect, "BACK", self.back_hovered)

    def _draw_image_btn(self, screen, img, rect, is_hovered):
        btn_img = img.copy()
        if is_hovered:
            btn_img.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(btn_img, rect)

    def _draw_text_btn(self, screen, rect, text, is_hovered):
        color = (100, 100, 150) if is_hovered else (70, 70, 100)
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 255), rect, 2, border_radius=10) # Border
        txt_surf = self.font.render(text, True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=rect.center)
        screen.blit(txt_surf, txt_rect)