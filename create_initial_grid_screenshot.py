"""Create a screenshot of initial grid state to verify coordinate mapping."""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from simulation import Simulation
from main import HexRenderer, COLORS


def create_initial_grid_screenshot():
    """Create a screenshot of the initial grid state."""
    print("Initializing pygame...")
    pygame.init()
    
    # Create display
    width, height = 1400, 900
    screen = pygame.display.set_mode((width, height))
    
    # Create simulation (but don't step it)
    print("Creating simulation...")
    sim = Simulation()
    
    # Render
    print("Rendering initial state...")
    screen.fill(COLORS['white'])
    
    renderer = HexRenderer(hex_size=20)
    renderer.origin = (400, 450)
    
    # Draw all hexes
    for hex_pos, cell in sim.grid.cells.items():
        # Determine color
        if cell.owner:
            color = COLORS[cell.owner]
        else:
            color = COLORS['yellow']
        
        # Draw hex with visual indicators
        is_permanent = cell.is_permanent
        is_protected = cell.is_protected(sim.current_hour)
        
        # Draw hex
        renderer.draw_hex(screen, hex_pos, color, COLORS['black'], 1, 
                         is_permanent=is_permanent, is_protected=is_protected)
    
    # Draw title and legend
    font = pygame.font.Font(None, 36)
    title = font.render("Initial Grid State - Coordinate-Based Mapping", True, COLORS['black'])
    screen.blit(title, (50, 20))
    
    # Draw legend
    legend_font = pygame.font.Font(None, 24)
    y_offset = 80
    
    legend_items = [
        ("Grey (22 hexes) - Permanent home base", COLORS['grey']),
        ("Orange (13 hexes) - Permanent home base", COLORS['orange']),
        ("Blue (13 hexes) - Permanent home base", COLORS['blue']),
        ("Green (13 hexes) - Permanent home base", COLORS['green']),
        ("Yellow - Unclaimed territory", COLORS['yellow'])
    ]
    
    for text, color in legend_items:
        # Draw color box
        pygame.draw.rect(screen, color, pygame.Rect(50, y_offset, 20, 20))
        pygame.draw.rect(screen, COLORS['black'], pygame.Rect(50, y_offset, 20, 20), 1)
        
        # Draw text
        label = legend_font.render(text, True, COLORS['black'])
        screen.blit(label, (80, y_offset))
        y_offset += 30
    
    # Draw counts
    grey_count = sum(1 for c in sim.grid.cells.values() if c.owner == 'grey' and c.is_permanent)
    orange_count = sum(1 for c in sim.grid.cells.values() if c.owner == 'orange' and c.is_permanent)
    blue_count = sum(1 for c in sim.grid.cells.values() if c.owner == 'blue' and c.is_permanent)
    green_count = sum(1 for c in sim.grid.cells.values() if c.owner == 'green' and c.is_permanent)
    total = grey_count + orange_count + blue_count + green_count
    
    y_offset += 20
    count_text = legend_font.render(f"Total Permanent Territories: {total}", True, COLORS['black'])
    screen.blit(count_text, (50, y_offset))
    
    # Save screenshot
    print("Saving screenshot...")
    pygame.image.save(screen, "initial_grid_coordinate_mapping.png")
    print("✓ Screenshot saved as initial_grid_coordinate_mapping.png")
    
    # Print verification
    print("\nInitial Grid Verification:")
    print(f"  Grey: {grey_count}/22")
    print(f"  Orange: {orange_count}/13")
    print(f"  Blue: {blue_count}/13")
    print(f"  Green: {green_count}/13")
    print(f"  Total: {total}/61")
    
    pygame.quit()


if __name__ == "__main__":
    create_initial_grid_screenshot()
