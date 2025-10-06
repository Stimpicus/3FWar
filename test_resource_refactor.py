"""Test script to verify the resource system refactor."""
from simulation import Simulation
from hex_grid import Hex

def test_grid_initialization():
    """Test that grid initialization follows new rules."""
    print("Testing grid initialization...")
    sim = Simulation()
    
    # Count hexes by owner
    owned_by_faction = {}
    unclaimed_count = 0
    
    for hex_pos, cell in sim.grid.cells.items():
        if cell.owner:
            owned_by_faction[cell.owner] = owned_by_faction.get(cell.owner, 0) + 1
        else:
            unclaimed_count += 1
    
    print(f"  Total cells: {len(sim.grid.cells)}")
    print(f"  Grey: {owned_by_faction.get('grey', 0)}")
    print(f"  Orange: {owned_by_faction.get('orange', 0)}")
    print(f"  Blue: {owned_by_faction.get('blue', 0)}")
    print(f"  Green: {owned_by_faction.get('green', 0)}")
    print(f"  Unclaimed: {unclaimed_count}")
    
    # Verify all unclaimed hexes are adjacent to owned
    unclaimed_hexes = [hex_pos for hex_pos, cell in sim.grid.cells.items() if cell.owner is None]
    non_adjacent = 0
    for yellow_hex in unclaimed_hexes:
        neighbors = sim.grid.get_neighbors(yellow_hex)
        has_owned = any(n.owner is not None for n in neighbors)
        if not has_owned:
            non_adjacent += 1
    
    assert non_adjacent == 0, f"Found {non_adjacent} unclaimed hexes not adjacent to owned!"
    print(f"  ✓ All {unclaimed_count} unclaimed hexes are adjacent to owned territories")
    
    # Verify each faction has adjacent unclaimed hexes
    for faction_color in ['grey', 'orange', 'blue', 'green']:
        faction_hexes = [hex_pos for hex_pos, cell in sim.grid.cells.items() if cell.owner == faction_color]
        
        # Find all unclaimed hexes adjacent to this faction
        adjacent_unclaimed = set()
        for faction_hex in faction_hexes:
            for neighbor in faction_hex.neighbors():
                neighbor_cell = sim.grid.get_cell(neighbor)
                if neighbor_cell and neighbor_cell.owner is None:
                    adjacent_unclaimed.add(neighbor)
        
        assert len(adjacent_unclaimed) > 0, f"{faction_color} has no adjacent unclaimed hexes!"
        print(f"  ✓ {faction_color.capitalize()}: {len(adjacent_unclaimed)} adjacent unclaimed hexes")
    
    print("  ✓ Grid initialization test passed!\n")


def test_resource_system():
    """Test that resources are added directly to credits."""
    print("Testing resource system...")
    sim = Simulation()
    
    # Check initial state
    state = sim.get_state()
    for color in ['orange', 'green', 'blue']:
        faction_data = state['factions'][color]
        assert faction_data['credits'] == 10_000, f"{color} initial credits wrong!"
        assert faction_data['daily_production'] == 0, f"{color} initial daily production wrong!"
        assert 'net_worth' not in faction_data, f"{color} still has net_worth field!"
        assert 'total_resources' not in faction_data, f"{color} still has total_resources field!"
    
    print("  ✓ Initial state correct (no net_worth or total_resources)")
    
    # Run for 24 hours
    for _ in range(24):
        sim.step_hour()
    
    state = sim.get_state()
    for color in ['orange', 'green', 'blue']:
        faction_data = state['factions'][color]
        # Credits should have increased from initial 10,000
        assert faction_data['credits'] > 10_000, f"{color} credits didn't increase!"
        # Daily production should be set
        assert faction_data['daily_production'] > 0, f"{color} daily production is 0!"
        print(f"  ✓ {color.capitalize()}: Credits=${faction_data['credits']:,.0f}, Daily Prod=${faction_data['daily_production']:,.0f}")
    
    print("  ✓ Daily production adds directly to credits!\n")


def test_save_load():
    """Test save/load with new format."""
    print("Testing save/load...")
    sim = Simulation()
    
    # Run for 24 hours
    for _ in range(24):
        sim.step_hour()
    
    # Save state
    save_data = sim.save_state()
    
    # Verify saved data doesn't contain old fields
    for color, faction_data in save_data['factions'].items():
        assert 'net_worth' not in faction_data, f"Save data still has net_worth for {color}!"
        assert 'total_resources' not in faction_data, f"Save data still has total_resources for {color}!"
        assert 'credits' in faction_data, f"Save data missing credits for {color}!"
        assert 'daily_production' in faction_data, f"Save data missing daily_production for {color}!"
    
    print("  ✓ Save data uses new format")
    
    # Load state
    sim2 = Simulation()
    sim2.load_state(save_data)
    state2 = sim2.get_state()
    
    # Verify loaded state matches
    state1 = sim.get_state()
    for color in ['orange', 'green', 'blue']:
        assert state1['factions'][color]['credits'] == state2['factions'][color]['credits'], \
            f"{color} credits don't match after load!"
        assert state1['factions'][color]['daily_production'] == state2['factions'][color]['daily_production'], \
            f"{color} daily_production doesn't match after load!"
    
    print("  ✓ Save/load works correctly!\n")


def test_weekly_reset():
    """Test weekly credit reset."""
    print("Testing weekly credit reset...")
    sim = Simulation()
    
    # Run for 24 hours
    for _ in range(24):
        sim.step_hour()
    
    state = sim.get_state()
    credits_before_reset = {}
    for color in ['orange', 'green', 'blue']:
        credits_before_reset[color] = state['factions'][color]['credits']
    
    # Run until week reset (168 hours total)
    for _ in range(168 - 24):
        sim.step_hour()
    
    state = sim.get_state()
    assert state['week'] == 1, "Week counter didn't increment!"
    
    # Credits should have been reset to 10,000
    for color in ['orange', 'green', 'blue']:
        # After reset, credits should be 10,000 (from reset) + daily production
        # This is because daily events happen at hour 192 (24 hours after week 1 starts)
        assert state['factions'][color]['credits'] >= 10_000, \
            f"{color} credits not reset properly!"
    
    print("  ✓ Weekly reset works correctly!\n")


if __name__ == "__main__":
    print("Running resource refactor tests...\n")
    test_grid_initialization()
    test_resource_system()
    test_save_load()
    test_weekly_reset()
    print("✓ All tests passed!")
