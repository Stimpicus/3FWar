"""Create a screenshot of the simulation for demonstration."""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from simulation import Simulation
from main import HexRenderer, COLORS


def create_screenshot():
    """Create a screenshot of the simulation."""
    print("Initializing pygame...")
    pygame.init()
    
    # Create display
    width, height = 1400, 900
    screen = pygame.display.set_mode((width, height))
    
    # Create simulation
    print("Creating simulation...")
    sim = Simulation()
    
    # Run simulation for a few hours to show some activity
    print("Running simulation for 48 hours...")
    for i in range(48):
        sim.step_hour()
    
    # Render
    print("Rendering...")
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
        
        # Draw hex
        renderer.draw_hex(screen, hex_pos, color, COLORS['black'], 1)
    
    # Draw UI info
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 20)
    
    # Draw panel background
    panel_rect = pygame.Rect(1000, 0, 400, 900)
    pygame.draw.rect(screen, COLORS['ui_bg'], panel_rect)
    pygame.draw.rect(screen, COLORS['ui_border'], panel_rect, 2)
    
    # Get state
    state = sim.get_state()
    
    y_offset = 10
    x_offset = 1010
    
    # Title
    title = font.render("3FWar Simulation", True, COLORS['black'])
    screen.blit(title, (x_offset, y_offset))
    y_offset += 30
    
    # Time
    time_text = small_font.render(
        f"Week: {state['week']} | Day: {state['day']} | Hour: {state['hour']}", 
        True, COLORS['black']
    )
    screen.blit(time_text, (x_offset, y_offset))
    y_offset += 25
    
    # Status
    status_text = small_font.render("RUNNING (Speed: 1x)", True, COLORS['green'])
    screen.blit(status_text, (x_offset, y_offset))
    y_offset += 30
    
    # Mercenary pool
    merc_text = small_font.render(
        f"Mercenary Pool: {state['mercenary_pool']}", 
        True, COLORS['black']
    )
    screen.blit(merc_text, (x_offset, y_offset))
    y_offset += 30
    
    # Faction info
    for color in ['orange', 'green', 'blue']:
        faction_data = state['factions'][color]
        
        # Faction name
        name_text = font.render(color.capitalize(), True, COLORS[color])
        screen.blit(name_text, (x_offset, y_offset))
        y_offset += 25
        
        # Net worth
        worth_text = small_font.render(
            f"  Net Worth: ${faction_data['net_worth']:,.0f}", 
            True, COLORS['black']
        )
        screen.blit(worth_text, (x_offset, y_offset))
        y_offset += 20
        
        # Credits
        credits_text = small_font.render(
            f"  Credits: ${faction_data['credits']:,.0f}", 
            True, COLORS['black']
        )
        screen.blit(credits_text, (x_offset, y_offset))
        y_offset += 20
        
        # Daily production
        prod_text = small_font.render(
            f"  Daily Prod: ${faction_data['daily_production']:,.0f}", 
            True, COLORS['black']
        )
        screen.blit(prod_text, (x_offset, y_offset))
        y_offset += 20
        
        # Territory count
        terr_text = small_font.render(
            f"  Territories: {faction_data['territory_count']}", 
            True, COLORS['black']
        )
        screen.blit(terr_text, (x_offset, y_offset))
        y_offset += 30
    
    # Controls
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
        control_text = small_font.render(control, True, COLORS['dark_grey'])
        screen.blit(control_text, (x_offset, y_offset))
        y_offset += 20
    
    # Save screenshot
    print("Saving screenshot...")
    pygame.image.save(screen, "simulation_screenshot.png")
    print("✓ Screenshot saved as simulation_screenshot.png")
    
    # Print state summary
    print("\nSimulation State:")
    print(f"  Time: Week {state['week']}, Day {state['day']}, Hour {state['hour']}")
    print(f"  Mercenaries: {state['mercenary_pool']}")
    for color, data in state['factions'].items():
        print(f"\n  {color.capitalize()}:")
        print(f"    Net Worth: ${data['net_worth']:,.0f}")
        print(f"    Territories: {data['territory_count']}")
    
    pygame.quit()


if __name__ == "__main__":
    create_screenshot()
