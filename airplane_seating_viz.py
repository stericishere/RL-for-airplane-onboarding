import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 130, 180)  # Blue seats
GRAY = (200, 200, 200)  # Empty seats
DARK_GRAY = (64, 64, 64)
RED = (220, 20, 60)  # Loading area
GREEN = (34, 139, 34)
YELLOW = (255, 215, 0)  # Passengers
ORANGE = (255, 165, 0)
LIGHT_GRAY = (230, 230, 230)

class Seat:
    def __init__(self, x, y, seat_id, has_passenger=False):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.seat_id = seat_id
        self.has_passenger = has_passenger
        self.has_luggage = has_passenger
        self.color = BLUE
        
    def draw(self, screen):
        # Draw seat
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        # Draw seat number
        font = pygame.font.Font(None, 16)
        if self.seat_id:
            text = font.render(str(self.seat_id), True, WHITE)
            text_rect = text.get_rect(center=(self.x + self.width//2, self.y + self.height - 8))
            screen.blit(text, text_rect)
        
        # Draw passenger if present
        if self.has_passenger:
            # Draw passenger face (yellow circle)
            center_x = self.x + self.width//2
            center_y = self.y + self.height//2 - 5
            pygame.draw.circle(screen, YELLOW, (center_x, center_y), 12)
            pygame.draw.circle(screen, BLACK, (center_x, center_y), 12, 2)
            
            # Draw simple smile
            pygame.draw.arc(screen, BLACK, (center_x - 8, center_y - 4, 16, 12), 0, math.pi, 2)
            
            # Draw eyes
            pygame.draw.circle(screen, BLACK, (center_x - 4, center_y - 3), 2)
            pygame.draw.circle(screen, BLACK, (center_x + 4, center_y - 3), 2)
        
        # Draw luggage if present
        if self.has_luggage:
            luggage_x = self.x + self.width//2 - 8
            luggage_y = self.y + self.height - 12
            pygame.draw.rect(screen, BLACK, (luggage_x, luggage_y, 16, 8))
            pygame.draw.rect(screen, DARK_GRAY, (luggage_x + 1, luggage_y + 1, 14, 6))

class LoadingArea:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.luggage_items = []
        
    def draw(self, screen):
        # Draw loading area background
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 3)
        
        # Draw label
        font = pygame.font.Font(None, 24)
        text = font.render("LOADING AREA", True, WHITE)
        text_rect = text.get_rect(center=(self.x + self.width//2, self.y + 20))
        screen.blit(text, text_rect)
        
        # Draw luggage in loading area
        for i, luggage in enumerate(self.luggage_items):
            lug_x = self.x + 20 + (i % 8) * 25
            lug_y = self.y + 40 + (i // 8) * 20
            pygame.draw.rect(screen, BLACK, (lug_x, lug_y, 20, 15))
            pygame.draw.rect(screen, DARK_GRAY, (lug_x + 1, lug_y + 1, 18, 13))

class AirplaneSeatingViz:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Airplane Seating Layout Visualization")
        self.clock = pygame.time.Clock()
        
        self.seats = []
        self.loading_area = LoadingArea(50, 600, 400, 150)
        self.total_passengers = 0
        self.total_luggage = 0
        
        self.setup_seating_layout()
        
    def setup_seating_layout(self):
        # Based on the screenshot layout
        start_x = 100
        start_y = 100
        seat_spacing = 50
        
        # Left section (3 columns)
        left_seats = [
            # Row format: [seat_numbers] with passenger info
            [45, 44, 43, None, None],  # First row
            [19, 18, 17, 16, None],    # passengers in 16
            [24, 23, 22, 21, 20],     # passengers in 20, 21, 22, 23, 24
            [29, 28, 27, 26, 25],     # passengers in 28, 29
            [34, 33, 32, 31, 30],     # passengers in 33, 34
            [39, 38, 37, 36, 35],     # passengers in 37, 32, 38, 39
            [44, 43, 42, 41, 40],     # passengers in 41, 42, 23, 43, 44
            [None, None, None, 36, 35], # passengers in 36
            # Bottom row
        ]
        
        # Passengers data based on screenshot
        passengers_seats = {
            3, 4, 5, 18, 28, 29, 33, 34, 37, 2, 38, 39, 
            41, 42, 23, 43, 44, 36, 18, 40, 31, 27, 49, 22, 48, 21,
            0, 1, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 20, 25, 26, 30, 35, 45, 46, 47, 14
        }
        
        # Create left section seats
        for row_idx, row in enumerate(left_seats):
            for col_idx, seat_num in enumerate(row):
                if seat_num is not None:
                    x = start_x + col_idx * seat_spacing
                    y = start_y + row_idx * seat_spacing
                    has_passenger = seat_num in passengers_seats
                    seat = Seat(x, y, seat_num, has_passenger)
                    self.seats.append(seat)
                    if has_passenger:
                        self.total_passengers += 1
                        self.total_luggage += 1
        
        # Create middle section (2 columns)
        middle_x = start_x + 6 * seat_spacing
        middle_seats = [
            [3, 4],    # passengers
            [5, None], # passenger in 5
            [None, None],
            [None, None],
            [None, None],
            [None, None],
            [None, None],
            [None, None],
        ]
        
        for row_idx, row in enumerate(middle_seats):
            for col_idx, seat_num in enumerate(row):
                if seat_num is not None:
                    x = middle_x + col_idx * seat_spacing
                    y = start_y + row_idx * seat_spacing
                    has_passenger = seat_num in passengers_seats
                    seat = Seat(x, y, seat_num, has_passenger)
                    self.seats.append(seat)
                    if has_passenger:
                        self.total_passengers += 1
                        self.total_luggage += 1
        
        # Create right section (5x8 grid)
        right_x = start_x + 9 * seat_spacing
        right_seats = [
            [0, 1, None, None, None],     # passengers in 0, 1
            [7, 8, 9, None, None],        # passengers in 7, 8, 9
            [10, 11, 12, 13, None],       # passengers in 10, 11, 12, 13
            [15, 16, 17, None, None],     # passengers in 15, 16, 17
            [20, None, None, None, None], # passenger in 20
            [25, 26, None, None, None],   # passengers in 25, 26
            [30, None, None, None, None], # passenger in 30
            [35, None, None, None, None], # passenger in 35
            [None, None, None, None, None],
            [45, 46, 47, None, None],     # passengers in 45, 46, 47
            [14, None, None, None, None], # passenger in 14 (bottom row)
        ]
        
        for row_idx, row in enumerate(right_seats):
            for col_idx, seat_num in enumerate(row):
                if seat_num is not None:
                    x = right_x + col_idx * seat_spacing
                    y = start_y + row_idx * seat_spacing
                    has_passenger = seat_num in passengers_seats
                    seat = Seat(x, y, seat_num, has_passenger)
                    self.seats.append(seat)
                    if has_passenger:
                        self.total_passengers += 1
                        self.total_luggage += 1
        
        # Add luggage items to loading area
        for _ in range(self.total_luggage):
            self.loading_area.luggage_items.append("luggage")
    
    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw title
        font = pygame.font.Font(None, 48)
        title = font.render("Airplane Seating Layout", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 30))
        self.screen.blit(title, title_rect)
        
        # Draw airplane outline
        airplane_x = 80
        airplane_y = 80
        airplane_width = 750
        airplane_height = 450
        pygame.draw.rect(self.screen, LIGHT_GRAY, (airplane_x, airplane_y, airplane_width, airplane_height), 3)
        
        # Draw all seats
        for seat in self.seats:
            seat.draw(self.screen)
        
        # Draw loading area
        self.loading_area.draw(self.screen)
        
        # Draw statistics
        font = pygame.font.Font(None, 24)
        stats_y = 550
        
        passenger_text = font.render(f"Total Passengers: {self.total_passengers}", True, BLACK)
        self.screen.blit(passenger_text, (500, stats_y))
        
        luggage_text = font.render(f"Luggage Items: {self.total_luggage}", True, BLACK)
        self.screen.blit(luggage_text, (500, stats_y + 30))
        
        # Draw legend
        legend_x = 900
        legend_y = 200
        font = pygame.font.Font(None, 20)
        
        legend_text = font.render("LEGEND:", True, BLACK)
        self.screen.blit(legend_text, (legend_x, legend_y))
        
        # Blue seat with passenger
        pygame.draw.rect(self.screen, BLUE, (legend_x, legend_y + 30, 30, 30))
        pygame.draw.rect(self.screen, BLACK, (legend_x, legend_y + 30, 30, 30), 2)
        pygame.draw.circle(self.screen, YELLOW, (legend_x + 15, legend_y + 40), 8)
        legend_text = font.render("Occupied Seat", True, BLACK)
        self.screen.blit(legend_text, (legend_x + 40, legend_y + 35))
        
        # Empty seat
        pygame.draw.rect(self.screen, BLUE, (legend_x, legend_y + 70, 30, 30))
        pygame.draw.rect(self.screen, BLACK, (legend_x, legend_y + 70, 30, 30), 2)
        legend_text = font.render("Empty Seat", True, BLACK)
        self.screen.blit(legend_text, (legend_x + 40, legend_y + 75))
        
        # Loading area
        pygame.draw.rect(self.screen, RED, (legend_x, legend_y + 110, 30, 20))
        pygame.draw.rect(self.screen, BLACK, (legend_x, legend_y + 110, 30, 20), 2)
        legend_text = font.render("Loading Area", True, BLACK)
        self.screen.blit(legend_text, (legend_x + 40, legend_y + 115))
        
        # Instructions
        instructions = [
            "Yellow faces = Passengers",
            "Black rectangles = Luggage",
            "Red area = Loading zone",
            "Blue rectangles = Seats"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, BLACK)
            self.screen.blit(text, (20, 20 + i * 25))
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    visualization = AirplaneSeatingViz()
    visualization.run()