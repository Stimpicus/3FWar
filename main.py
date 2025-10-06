"""Main pygame application for 3FWar simulation."""
import pygame
import sys
import json
import math
from typing import Tuple, Optional
from simulation import Simulation
from hex_grid import Hex


# Color definitions
COLORS = {
    'grey': (180, 180, 180),
    'orange': (255, 165, 0),
    'green': (34, 139, 34),
    'blue': (30, 144, 255),
    'yellow': (255, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'dark_grey': (50, 50, 50),
    'light_grey': (200, 200, 200),
    'ui_bg': (240, 240, 240),
    'ui_border': (100, 100, 100)
}


class HexRenderer:
    """Handles rendering of hex grid."""
    
    def __init__(self, hex_size: float = 20):
        self.hex_size = hex_size
        self.origin = (400, 400)  # Center of screen
    
    def hex_to_pixel(self, hex_pos: Hex) -> Tuple[float, float]:
        """Convert hex coordinates to pixel coordinates."""
        return hex_pos.to_pixel(self.hex_size, self.origin)
    
    def pixel_to_hex(self, pixel: Tuple[float, float]) -> Hex:
        """Convert pixel coordinates to hex coordinates (approximate)."""
        x = pixel[0] - self.origin[0]
        y = pixel[1] - self.origin[1]
        
        q = (2./3 * x) / self.hex_size
        r = (-1./3 * x + math.sqrt(3)/3 * y) / self.hex_size
        
        return self.hex_round(q, r)
    
    def hex_round(self, q: float, r: float) -> Hex:
        """Round fractional hex coordinates to nearest hex."""
        s = -q - r
        
        q_int = round(q)
        r_int = round(r)
        s_int = round(s)
        
        q_diff = abs(q_int - q)
        r_diff = abs(r_int - r)
        s_diff = abs(s_int - s)
        
        if q_diff > r_diff and q_diff > s_diff:
            q_int = -r_int - s_int
        elif r_diff > s_diff:
            r_int = -q_int - s_int
        
        return Hex(q_int, r_int)
    
    def get_hex_corners(self, center: Tuple[float, float]) -> list:
        """Get the 6 corner points of a hexagon."""
        corners = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            x = center[0] + self.hex_size * math.cos(angle_rad)
            y = center[1] + self.hex_size * math.sin(angle_rad)
            corners.append((x, y))
        return corners
    
    def draw_hex(self, surface: pygame.Surface, hex_pos: Hex, color: Tuple[int, int, int], 
                 border_color: Tuple[int, int, int] = None, border_width: int = 2,
                 is_permanent: bool = False, is_protected: bool = False):
        """Draw a hexagon on the surface with optional icons."""
        center = self.hex_to_pixel(hex_pos)
        corners = self.get_hex_corners(center)
        
        # Draw filled hexagon
        pygame.draw.polygon(surface, color, corners)
        
        # Draw border
        if border_color:
            pygame.draw.polygon(surface, border_color, corners, border_width)
        
        # Draw Lock icon for permanent territories
        if is_permanent:
            self.draw_lock_icon(surface, center)
        
        # Draw Shield icon for protected territories
        if is_protected:
            self.draw_shield_icon(surface, center)
    
    def draw_lock_icon(self, surface: pygame.Surface, center: Tuple[float, float]):
        """Draw a lock icon at the center of a hex."""
        # Simple lock using rectangles and a circle
        lock_size = self.hex_size * 0.4
        
        # Lock body (rectangle)
        body_width = lock_size * 0.6
        body_height = lock_size * 0.5
        body_rect = pygame.Rect(
            center[0] - body_width / 2,
            center[1] - body_height / 4,
            body_width,
            body_height
        )
        pygame.draw.rect(surface, COLORS['black'], body_rect)
        pygame.draw.rect(surface, COLORS['white'], body_rect, 1)
        
        # Lock shackle (arc)
        shackle_radius = lock_size * 0.25
        shackle_center = (center[0], center[1] - body_height / 4)
        pygame.draw.arc(
            surface,
            COLORS['black'],
            pygame.Rect(
                shackle_center[0] - shackle_radius,
                shackle_center[1] - shackle_radius * 1.5,
                shackle_radius * 2,
                shackle_radius * 2
            ),
            math.pi,
            0,
            3
        )
        
        # Keyhole (small circle)
        keyhole_radius = lock_size * 0.08
        pygame.draw.circle(surface, COLORS['white'], 
                         (int(center[0]), int(center[1] + lock_size * 0.05)), 
                         int(keyhole_radius))
    
    def draw_shield_icon(self, surface: pygame.Surface, center: Tuple[float, float]):
        """Draw a shield icon at the center of a hex."""
        # Simple shield shape using polygon
        shield_size = self.hex_size * 0.4
        
        # Shield points (pentagon-like shape)
        points = [
            (center[0], center[1] - shield_size / 2),  # Top
            (center[0] + shield_size / 2, center[1] - shield_size / 4),  # Top-right
            (center[0] + shield_size / 2, center[1] + shield_size / 4),  # Bottom-right
            (center[0], center[1] + shield_size / 2),  # Bottom point
            (center[0] - shield_size / 2, center[1] + shield_size / 4),  # Bottom-left
            (center[0] - shield_size / 2, center[1] - shield_size / 4),  # Top-left
        ]
        
        # Draw shield with blue color
        pygame.draw.polygon(surface, COLORS['blue'], points)
        pygame.draw.polygon(surface, COLORS['white'], points, 2)
        
        # Draw cross in center for extra detail
        cross_size = shield_size * 0.3
        pygame.draw.line(surface, COLORS['white'],
                        (center[0] - cross_size / 2, center[1]),
                        (center[0] + cross_size / 2, center[1]), 2)
        pygame.draw.line(surface, COLORS['white'],
                        (center[0], center[1] - cross_size / 2),
                        (center[0], center[1] + cross_size / 2), 2)


class UIPanel:
    """UI panel for displaying simulation information and controls."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
    
    def draw(self, surface: pygame.Surface, simulation: Simulation, paused: bool, speed: int):
        """Draw the UI panel."""
        # Draw background
        pygame.draw.rect(surface, COLORS['ui_bg'], self.rect)
        pygame.draw.rect(surface, COLORS['ui_border'], self.rect, 2)
        
        # Get simulation state
        state = simulation.get_state()
        
        y_offset = self.rect.y + 10
        x_offset = self.rect.x + 10
        
        # Draw title
        title = self.font.render("3FWar Simulation", True, COLORS['black'])
        surface.blit(title, (x_offset, y_offset))
        y_offset += 30
        
        # Draw time info
        time_text = self.small_font.render(
            f"Week: {state['week']} | Day: {state['day']} | Hour: {state['hour']}", 
            True, COLORS['black']
        )
        surface.blit(time_text, (x_offset, y_offset))
        y_offset += 25
        
        # Draw status
        status = "PAUSED" if paused else f"RUNNING (Speed: {speed}x)"
        status_color = COLORS['orange'] if paused else COLORS['green']
        status_text = self.small_font.render(status, True, status_color)
        surface.blit(status_text, (x_offset, y_offset))
        y_offset += 30
        
        # Draw mercenary pool
        merc_text = self.small_font.render(
            f"Mercenary Pool: {state['mercenary_pool']}", 
            True, COLORS['black']
        )
        surface.blit(merc_text, (x_offset, y_offset))
        y_offset += 30
        
        # Draw faction info
        for color in ['orange', 'green', 'blue']:
            faction_data = state['factions'][color]
            
            # Faction name
            name_text = self.font.render(color.capitalize(), True, COLORS[color])
            surface.blit(name_text, (x_offset, y_offset))
            y_offset += 25
            
            # Credits
            credits_text = self.small_font.render(
                f"  Credits: ${faction_data['credits']:,.0f}", 
                True, COLORS['black']
            )
            surface.blit(credits_text, (x_offset, y_offset))
            y_offset += 20
            
            # Daily production
            prod_text = self.small_font.render(
                f"  Daily Prod: ${faction_data['daily_production']:,.0f}", 
                True, COLORS['black']
            )
            surface.blit(prod_text, (x_offset, y_offset))
            y_offset += 20
            
            # Territory count
            terr_text = self.small_font.render(
                f"  Territories: {faction_data['territory_count']}", 
                True, COLORS['black']
            )
            surface.blit(terr_text, (x_offset, y_offset))
            y_offset += 30
        
        # Draw controls info
        y_offset += 10
        controls = [
            "Controls:",
            "SPACE - Start/Pause",
            "R - Reset",
            "S - Save",
            "L - Load",
            "+/- - Speed",
            "Arrow Keys - Pan",
            "Mouse Wheel - Zoom"
        ]
        
        for control in controls:
            control_text = self.small_font.render(control, True, COLORS['dark_grey'])
            surface.blit(control_text, (x_offset, y_offset))
            y_offset += 20


class Application:
    """Main application class."""
    
    def __init__(self):
        pygame.init()
        
        # Window setup
        self.width = 1400
        self.height = 900
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("3FWar - Territory Control Simulation")
        
        # Simulation
        self.simulation = Simulation()
        
        # Rendering
        self.renderer = HexRenderer(hex_size=20)
        self.ui_panel = UIPanel(1000, 0, 400, 900)
        
        # State
        self.running = True
        self.paused = True
        self.speed = 1  # 0-4 scale
        self.clock = pygame.time.Clock()
        self.time_accumulator = 0.0
        
        # Camera
        self.camera_offset = [0, 0]
        self.zoom = 1.0
        
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                
                elif event.key == pygame.K_r:
                    self.simulation.reset()
                    self.paused = True
                
                elif event.key == pygame.K_s:
                    self.save_simulation()
                
                elif event.key == pygame.K_l:
                    self.load_simulation()
                
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    self.speed = min(4, self.speed + 1)
                
                elif event.key == pygame.K_MINUS:
                    self.speed = max(0, self.speed - 1)
                
                # Camera controls
                elif event.key == pygame.K_LEFT:
                    self.camera_offset[0] += 50
                elif event.key == pygame.K_RIGHT:
                    self.camera_offset[0] -= 50
                elif event.key == pygame.K_UP:
                    self.camera_offset[1] += 50
                elif event.key == pygame.K_DOWN:
                    self.camera_offset[1] -= 50
            
            elif event.type == pygame.MOUSEWHEEL:
                # Zoom with mouse wheel
                if event.y > 0:
                    self.zoom *= 1.1
                elif event.y < 0:
                    self.zoom /= 1.1
                
                self.zoom = max(0.3, min(3.0, self.zoom))
                self.renderer.hex_size = 20 * self.zoom
    
    def update(self, dt: float):
        """Update simulation."""
        if not self.paused and self.speed > 0:
            # Speed scale: 0 = paused, 1 = 1 hour/sec, 2 = 2 hours/sec, etc.
            self.time_accumulator += dt * self.speed
            
            # Each hour should take 1 second at speed 1
            while self.time_accumulator >= 1.0:
                self.simulation.step_hour()
                self.time_accumulator -= 1.0
    
    def render(self):
        """Render the application."""
        self.screen.fill(COLORS['white'])
        
        # Apply camera offset
        old_origin = self.renderer.origin
        self.renderer.origin = (
            old_origin[0] + self.camera_offset[0],
            old_origin[1] + self.camera_offset[1]
        )
        
        # Draw all hexes
        for hex_pos, cell in self.simulation.grid.cells.items():
            # Determine color
            if cell.owner:
                color = COLORS[cell.owner]
            else:
                color = COLORS['yellow']
            
            # Check if protected
            is_protected = cell.is_protected(self.simulation.current_hour)
            
            # Draw hex with icons
            self.renderer.draw_hex(self.screen, hex_pos, color, COLORS['black'], 1,
                                  is_permanent=cell.is_permanent,
                                  is_protected=is_protected)
        
        # Restore origin
        self.renderer.origin = old_origin
        
        # Draw UI panel
        self.ui_panel.draw(self.screen, self.simulation, self.paused, self.speed)
        
        pygame.display.flip()
    
    def save_simulation(self):
        """Save simulation state to file."""
        try:
            state = self.simulation.save_state()
            with open('simulation_save.json', 'w') as f:
                json.dump(state, f, indent=2)
            print("Simulation saved to simulation_save.json")
        except Exception as e:
            print(f"Error saving simulation: {e}")
    
    def load_simulation(self):
        """Load simulation state from file."""
        try:
            with open('simulation_save.json', 'r') as f:
                state = json.load(f)
            self.simulation.load_state(state)
            self.paused = True
            print("Simulation loaded from simulation_save.json")
        except FileNotFoundError:
            print("No save file found")
        except Exception as e:
            print(f"Error loading simulation: {e}")
    
    def run(self):
        """Main application loop."""
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.render()
        
        pygame.quit()
        sys.exit()


def main():
    """Entry point."""
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
