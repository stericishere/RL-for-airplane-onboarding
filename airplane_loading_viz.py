import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 130, 180)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
YELLOW = (255, 215, 0)
ORANGE = (255, 165, 0)

class Cargo:
    def __init__(self, x, y, width, height, weight, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.weight = weight
        self.color = color
        self.loaded = False
        self.target_x = x
        self.target_y = y
        
    def move_towards_target(self, speed=2):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > speed:
            self.x += (dx / distance) * speed
            self.y += (dy / distance) * speed
        else:
            self.x = self.target_x
            self.y = self.target_y
            
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        # Draw weight label
        font = pygame.font.Font(None, 20)
        text = font.render(f"{self.weight}kg", True, WHITE)
        text_rect = text.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
        screen.blit(text, text_rect)

class Airplane:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 400
        self.height = 120
        self.cargo_compartments = []
        self.max_weight = 5000
        self.current_weight = 0
        
        # Define cargo compartment positions
        compartment_width = 60
        compartment_height = 40
        for i in range(5):
            comp_x = self.x + 50 + i * (compartment_width + 10)
            comp_y = self.y + 40
            self.cargo_compartments.append({
                'x': comp_x, 
                'y': comp_y, 
                'width': compartment_width, 
                'height': compartment_height,
                'occupied': False,
                'cargo': None
            })
    
    def draw(self, screen):
        # Draw airplane body
        pygame.draw.ellipse(screen, GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.ellipse(screen, BLACK, (self.x, self.y, self.width, self.height), 3)
        
        # Draw nose
        pygame.draw.polygon(screen, DARK_GRAY, [
            (self.x + self.width, self.y + self.height//2 - 20),
            (self.x + self.width + 40, self.y + self.height//2),
            (self.x + self.width, self.y + self.height//2 + 20)
        ])
        
        # Draw wing
        pygame.draw.ellipse(screen, GRAY, (self.x + 150, self.y - 30, 100, 40))
        pygame.draw.ellipse(screen, BLACK, (self.x + 150, self.y - 30, 100, 40), 2)
        
        # Draw cargo compartments
        for comp in self.cargo_compartments:
            color = GREEN if not comp['occupied'] else RED
            pygame.draw.rect(screen, color, (comp['x'], comp['y'], comp['width'], comp['height']))
            pygame.draw.rect(screen, BLACK, (comp['x'], comp['y'], comp['width'], comp['height']), 2)
        
        # Draw weight indicator
        font = pygame.font.Font(None, 36)
        weight_text = font.render(f"Weight: {self.current_weight}/{self.max_weight}kg", True, BLACK)
        screen.blit(weight_text, (self.x, self.y - 50))
        
        # Draw weight bar
        bar_width = 300
        bar_height = 20
        bar_x = self.x + 50
        bar_y = self.y - 25
        
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Fill weight bar
        fill_width = (self.current_weight / self.max_weight) * bar_width
        if fill_width > 0:
            color = GREEN if self.current_weight <= self.max_weight * 0.8 else YELLOW if self.current_weight <= self.max_weight else RED
            pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))

class LoadingSimulation:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Airplane Loading Visualization")
        self.clock = pygame.time.Clock()
        
        self.airplane = Airplane(200, 300)
        self.cargo_items = []
        self.loading_queue = []
        self.loading_in_progress = False
        
        # Create some cargo items
        cargo_weights = [500, 800, 300, 1200, 600, 400, 900, 700]
        cargo_colors = [RED, GREEN, BLUE, YELLOW, ORANGE, GRAY, DARK_GRAY, (255, 192, 203)]
        
        for i, (weight, color) in enumerate(zip(cargo_weights, cargo_colors)):
            cargo = Cargo(50, 100 + i * 60, 40, 40, weight, color)
            self.cargo_items.append(cargo)
        
    def find_available_compartment(self):
        for comp in self.airplane.cargo_compartments:
            if not comp['occupied']:
                return comp
        return None
    
    def start_loading(self):
        if not self.loading_in_progress and self.cargo_items:
            # Find next unloaded cargo
            for cargo in self.cargo_items:
                if not cargo.loaded:
                    # Check weight limit
                    if self.airplane.current_weight + cargo.weight <= self.airplane.max_weight:
                        comp = self.find_available_compartment()
                        if comp:
                            cargo.target_x = comp['x'] + 10
                            cargo.target_y = comp['y'] + 5
                            comp['occupied'] = True
                            comp['cargo'] = cargo
                            self.airplane.current_weight += cargo.weight
                            self.loading_in_progress = True
                            break
    
    def update(self):
        if self.loading_in_progress:
            # Find cargo being loaded
            for cargo in self.cargo_items:
                if not cargo.loaded and (cargo.x != cargo.target_x or cargo.y != cargo.target_y):
                    cargo.move_towards_target()
                    if abs(cargo.x - cargo.target_x) < 1 and abs(cargo.y - cargo.target_y) < 1:
                        cargo.loaded = True
                        self.loading_in_progress = False
                    break
    
    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw title
        font = pygame.font.Font(None, 48)
        title = font.render("Airplane Cargo Loading Simulation", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title, title_rect)
        
        # Draw instructions
        font = pygame.font.Font(None, 24)
        instructions = [
            "Click 'LOAD' to load next cargo item",
            "Red compartments = occupied, Green = available",
            "Weight limit: 5000kg"
        ]
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, BLACK)
            self.screen.blit(text, (20, SCREEN_HEIGHT - 80 + i * 25))
        
        # Draw load button
        button_rect = pygame.Rect(50, 50, 100, 40)
        pygame.draw.rect(self.screen, GREEN, button_rect)
        pygame.draw.rect(self.screen, BLACK, button_rect, 2)
        
        font = pygame.font.Font(None, 24)
        button_text = font.render("LOAD", True, BLACK)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, button_text_rect)
        
        # Draw airplane
        self.airplane.draw(self.screen)
        
        # Draw cargo items
        for cargo in self.cargo_items:
            cargo.draw(self.screen)
        
        # Draw cargo queue label
        font = pygame.font.Font(None, 24)
        queue_label = font.render("Cargo Queue:", True, BLACK)
        self.screen.blit(queue_label, (20, 80))
    
    def handle_click(self, pos):
        button_rect = pygame.Rect(50, 50, 100, 40)
        if button_rect.collidepoint(pos):
            self.start_loading()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    simulation = LoadingSimulation()
    simulation.run()