import pygame
import sys
import numpy as np
import gymnasium as gym
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'RL ENV'))
from airplane_boarding import PassengerStatus
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.utils import get_action_masks

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
FPS = 2  # Slow enough to see agent decisions

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 130, 180)
GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
YELLOW = (255, 215, 0)
ORANGE = (255, 165, 0)
LIGHT_GRAY = (230, 230, 230)
PURPLE = (128, 0, 128)
LIGHT_BLUE = (173, 216, 230)

class RLBoardingVisualization:
    def __init__(self, model_path=None, num_rows=10, seats_per_row=5):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("RL Airplane Boarding Agent - Live Simulation")
        self.clock = pygame.time.Clock()
        
        self.num_rows = num_rows
        self.seats_per_row = seats_per_row
        
        # Initialize environment
        self.env = gym.make('airplane-boarding-v0', 
                           num_of_rows=num_rows, 
                           seats_per_row=seats_per_row, 
                           render_mode=None)
        
        # Load trained model if provided
        self.model = None
        if model_path:
            try:
                self.model = MaskablePPO.load(model_path, env=self.env)
                print(f"Loaded model from {model_path}")
            except Exception as e:
                print(f"Could not load model: {e}")
                self.model = None
        
        # Game state
        self.obs = None
        self.terminated = False
        self.total_reward = 0
        self.step_count = 0
        self.last_action = None
        self.action_masks = None
        
        # Visualization parameters
        self.seat_size = 35
        self.passenger_size = 20
        
        self.reset_simulation()
    
    def reset_simulation(self):
        """Reset the simulation to initial state"""
        self.obs, _ = self.env.reset()
        self.terminated = False
        self.total_reward = 0
        self.step_count = 0
        self.last_action = None
        self.action_masks = get_action_masks(self.env)
    
    def step_simulation(self):
        """Execute one step of the simulation"""
        if self.terminated:
            return
        
        if self.model:
            # Use trained agent
            action, _ = self.model.predict(
                observation=self.obs, 
                deterministic=True, 
                action_masks=self.action_masks
            )
        else:
            # Random agent fallback
            valid_actions = [i for i, mask in enumerate(self.action_masks) if mask]
            if valid_actions:
                action = np.random.choice(valid_actions)
            else:
                return
        
        # Store action for visualization
        self.last_action = action
        
        # Execute action
        self.obs, reward, self.terminated, _, _ = self.env.step(action)
        self.total_reward += reward
        self.step_count += 1
        
        if not self.terminated:
            self.action_masks = get_action_masks(self.env)
    
    def draw_lobby(self):
        """Draw the lobby area with waiting passengers"""
        lobby_x = 50
        lobby_y = 50
        lobby_width = 300
        lobby_height = 400
        
        # Draw lobby background
        pygame.draw.rect(self.screen, LIGHT_GRAY, (lobby_x, lobby_y, lobby_width, lobby_height))
        pygame.draw.rect(self.screen, BLACK, (lobby_x, lobby_y, lobby_width, lobby_height), 2)
        
        # Title
        font = pygame.font.Font(None, 24)
        title = font.render("LOBBY", True, BLACK)
        title_rect = title.get_rect(center=(lobby_x + lobby_width//2, lobby_y + 15))
        self.screen.blit(title, title_rect)
        
        # Draw lobby rows
        for row_idx, lobby_row in enumerate(self.env.unwrapped.lobby.lobby_rows):
            row_y = lobby_y + 40 + row_idx * 35
            row_x = lobby_x + 10
            
            # Row label
            font = pygame.font.Font(None, 20)
            row_label = font.render(f"Row {row_idx}:", True, BLACK)
            self.screen.blit(row_label, (row_x, row_y))
            
            # Passengers in this lobby row
            for pass_idx, passenger in enumerate(lobby_row.passengers):
                pass_x = row_x + 60 + pass_idx * 25
                pass_y = row_y
                
                # Highlight if this row was selected in last action
                color = GREEN if self.last_action == row_idx else YELLOW
                
                pygame.draw.circle(self.screen, color, (pass_x + 10, pass_y + 10), 8)
                pygame.draw.circle(self.screen, BLACK, (pass_x + 10, pass_y + 10), 8, 1)
                
                # Passenger number
                font = pygame.font.Font(None, 14)
                text = font.render(str(passenger.seat_num), True, BLACK)
                text_rect = text.get_rect(center=(pass_x + 10, pass_y + 10))
                self.screen.blit(text, text_rect)
    
    def draw_boarding_line(self):
        """Draw the boarding line (aisle)"""
        line_x = 400
        line_y = 100
        line_width = 60
        
        # Title
        font = pygame.font.Font(None, 24)
        title = font.render("BOARDING LINE", True, BLACK)
        self.screen.blit(title, (line_x, line_y - 30))
        
        # Draw each position in the boarding line
        for i, passenger in enumerate(self.env.unwrapped.boarding_line.line):
            pos_y = line_y + i * 40
            pos_x = line_x
            
            # Draw position rectangle
            if passenger is None:
                color = LIGHT_GRAY
            elif passenger.status == PassengerStatus.MOVING:
                color = GREEN
            elif passenger.status == PassengerStatus.STALLED:
                color = RED
            elif passenger.status == PassengerStatus.STOWING:
                color = ORANGE
            else:
                color = GRAY
            
            pygame.draw.rect(self.screen, color, (pos_x, pos_y, line_width, 35))
            pygame.draw.rect(self.screen, BLACK, (pos_x, pos_y, line_width, 35), 2)
            
            if passenger is not None:
                # Draw passenger
                center_x = pos_x + line_width // 2
                center_y = pos_y + 17
                pygame.draw.circle(self.screen, YELLOW, (center_x, center_y), 12)
                pygame.draw.circle(self.screen, BLACK, (center_x, center_y), 12, 1)
                
                # Passenger details
                font = pygame.font.Font(None, 12)
                seat_text = font.render(str(passenger.seat_num), True, BLACK)
                seat_rect = seat_text.get_rect(center=(center_x, center_y - 3))
                self.screen.blit(seat_text, seat_rect)
                
                status_str = str(passenger.status)
                if '.' in status_str:
                    status_display = status_str.split('.')[1][:3]
                else:
                    status_display = status_str[:3]
                status_text = font.render(status_display, True, BLACK)
                status_rect = status_text.get_rect(center=(center_x, center_y + 5))
                self.screen.blit(status_text, status_rect)
    
    def draw_airplane(self):
        """Draw the airplane seating area"""
        plane_x = 500
        plane_y = 100
        
        # Title
        font = pygame.font.Font(None, 24)
        title = font.render("AIRPLANE", True, BLACK)
        self.screen.blit(title, (plane_x, plane_y - 30))
        
        # Draw airplane rows
        for row_idx, airplane_row in enumerate(self.env.unwrapped.airplane_rows):
            row_y = plane_y + row_idx * 40
            row_x = plane_x
            
            # Row number
            font = pygame.font.Font(None, 16)
            row_label = font.render(f"R{row_idx}", True, BLACK)
            self.screen.blit(row_label, (row_x - 25, row_y + 10))
            
            # Draw seats in this row
            for seat_idx, seat in enumerate(airplane_row.seats):
                seat_x = row_x + seat_idx * (self.seat_size + 5)
                seat_y = row_y
                
                # Seat color based on occupancy
                if seat.passenger is None:
                    color = BLUE  # Empty seat
                else:
                    color = GREEN  # Occupied seat
                
                pygame.draw.rect(self.screen, color, (seat_x, seat_y, self.seat_size, self.seat_size))
                pygame.draw.rect(self.screen, BLACK, (seat_x, seat_y, self.seat_size, self.seat_size), 2)
                
                # Seat number
                font = pygame.font.Font(None, 12)
                seat_text = font.render(str(seat.seat_num), True, WHITE if seat.passenger is None else BLACK)
                seat_rect = seat_text.get_rect(center=(seat_x + self.seat_size//2, seat_y + self.seat_size - 8))
                self.screen.blit(seat_text, seat_rect)
                
                # Draw passenger if present
                if seat.passenger is not None:
                    center_x = seat_x + self.seat_size // 2
                    center_y = seat_y + self.seat_size // 2 - 5
                    pygame.draw.circle(self.screen, YELLOW, (center_x, center_y), 10)
                    pygame.draw.circle(self.screen, BLACK, (center_x, center_y), 10, 1)
    
    def draw_stats(self):
        """Draw simulation statistics"""
        stats_x = 50
        stats_y = 500
        
        font = pygame.font.Font(None, 24)
        
        # Title
        title = font.render("SIMULATION STATS", True, BLACK)
        self.screen.blit(title, (stats_x, stats_y))
        
        # Stats
        stats = [
            f"Step: {self.step_count}",
            f"Total Reward: {self.total_reward:.1f}",
            f"Last Action: Row {self.last_action}" if self.last_action is not None else "Last Action: None",
            f"Passengers in Lobby: {self.env.unwrapped.lobby.count_passengers()}",
            f"Passengers Stalled: {self.env.unwrapped.boarding_line.num_passengers_stalled()}",
            f"Passengers Moving: {self.env.unwrapped.boarding_line.num_passengers_moving()}",
            f"Status: {'BOARDING' if not self.terminated else 'COMPLETE'}"
        ]
        
        font = pygame.font.Font(None, 20)
        for i, stat in enumerate(stats):
            text = font.render(stat, True, BLACK)
            self.screen.blit(text, (stats_x, stats_y + 30 + i * 25))
    
    def draw_legend(self):
        """Draw color legend"""
        legend_x = 900
        legend_y = 200
        
        font = pygame.font.Font(None, 20)
        title = font.render("LEGEND", True, BLACK)
        self.screen.blit(title, (legend_x, legend_y))
        
        legend_items = [
            (GREEN, "Moving/Selected"),
            (RED, "Stalled"),
            (ORANGE, "Stowing Luggage"),
            (YELLOW, "Passenger"),
            (BLUE, "Empty Seat"),
            (LIGHT_GRAY, "Empty Position")
        ]
        
        font = pygame.font.Font(None, 16)
        for i, (color, description) in enumerate(legend_items):
            y_pos = legend_y + 30 + i * 25
            pygame.draw.rect(self.screen, color, (legend_x, y_pos, 20, 15))
            pygame.draw.rect(self.screen, BLACK, (legend_x, y_pos, 20, 15), 1)
            text = font.render(description, True, BLACK)
            self.screen.blit(text, (legend_x + 30, y_pos))
    
    def draw_instructions(self):
        """Draw control instructions"""
        inst_x = 900
        inst_y = 400
        
        font = pygame.font.Font(None, 20)
        title = font.render("CONTROLS", True, BLACK)
        self.screen.blit(title, (inst_x, inst_y))
        
        instructions = [
            "SPACE: Next Step",
            "R: Reset Simulation",
            "A: Auto Mode (toggle)",
            "Q: Quit"
        ]
        
        font = pygame.font.Font(None, 16)
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, BLACK)
            self.screen.blit(text, (inst_x, inst_y + 30 + i * 20))
    
    def draw(self):
        """Main drawing method"""
        self.screen.fill(WHITE)
        
        # Title
        font = pygame.font.Font(None, 36)
        title = font.render("RL Airplane Boarding Agent - Live Simulation", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 20))
        self.screen.blit(title, title_rect)
        
        # Draw all components
        self.draw_lobby()
        self.draw_boarding_line()
        self.draw_airplane()
        self.draw_stats()
        self.draw_legend()
        self.draw_instructions()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        auto_mode = False
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.step_simulation()
                    elif event.key == pygame.K_r:
                        self.reset_simulation()
                    elif event.key == pygame.K_a:
                        auto_mode = not auto_mode
                        print(f"Auto mode: {'ON' if auto_mode else 'OFF'}")
                    elif event.key == pygame.K_q:
                        running = False
            
            # Auto mode
            if auto_mode and not self.terminated:
                self.step_simulation()
            
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # Try to load a model if it exists
    model_path = None
    try:
        import os
        if os.path.exists("models/MaskablePPO"):
            # Look for the best model
            model_files = [f for f in os.listdir("models/MaskablePPO") if f.endswith('.zip')]
            if model_files:
                # Get the most recent model
                model_files.sort()
                model_path = f"models/MaskablePPO/{model_files[-1]}"
                print(f"Found model: {model_path}")
    except:
        pass
    
    # Create and run visualization
    viz = RLBoardingVisualization(model_path=model_path, num_rows=10, seats_per_row=5)
    viz.run()