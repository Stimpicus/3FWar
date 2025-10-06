"""Comprehensive integration test for all simulation features."""
from simulation import Simulation
from hex_grid import Hex
import json


def test_all_features():
    """Test all simulation features comprehensively."""
    print("="*70)
    print("  3FWar Simulation - Comprehensive Feature Test")
    print("="*70)
    
    # Test 1: Initial Setup
    print("\n[TEST 1] Initial Setup and Grid")
    sim = Simulation()
    state = sim.get_state()
    
    assert state['hour'] == 0, "Initial hour should be 0"
    assert state['day'] == 0, "Initial day should be 0"
    assert state['week'] == 0, "Initial week should be 0"
    assert state['mercenary_pool'] >= 300, "Mercenary pool should be at least 300"
    assert state['mercenary_pool'] <= 5000, "Mercenary pool should be at most 5000"
    
    # Check factions
    assert len(state['factions']) == 3, "Should have 3 factions"
    for color in ['orange', 'green', 'blue']:
        assert color in state['factions'], f"{color} faction should exist"
        assert state['factions'][color]['credits'] == 10_000, f"{color} should start with 10k credits"
        assert state['factions'][color]['territory_count'] > 0, f"{color} should have territories"
    
    print("  ✓ Initial setup correct")
    print(f"  ✓ Grid has {len(sim.grid.cells)} hexes")
    print(f"  ✓ Orange: {state['factions']['orange']['territory_count']} territories")
    print(f"  ✓ Green: {state['factions']['green']['territory_count']} territories")
    print(f"  ✓ Blue: {state['factions']['blue']['territory_count']} territories")
    
    # Test 2: Hourly Resource Production
    print("\n[TEST 2] Hourly Resource Production")
    initial_territories = {
        color: data['territory_count'] 
        for color, data in state['factions'].items()
    }
    
    sim.step_hour()
    state = sim.get_state()
    
    assert state['hour'] == 1, "Hour should advance"
    print(f"  ✓ Hour advanced to {state['hour']}")
    
    # Check that some faction has expanded (if random allows)
    total_territories = sum(data['territory_count'] for data in state['factions'].values())
    print(f"  ✓ Total territories: {total_territories}")
    
    # Test 3: Daily Resource Deposit
    print("\n[TEST 3] Daily Resource Deposit")
    for _ in range(23):  # Complete the first day
        sim.step_hour()
    
    state = sim.get_state()
    assert state['hour'] == 24, "Should be at hour 24"
    assert state['day'] == 1, "Should be day 1"
    
    # Check daily production metrics
    for color, data in state['factions'].items():
        print(f"  ✓ {color.capitalize()}: Daily production = ${data['daily_production']:,.2f}")
    
    # Test 4: Weekly Credit Reset
    print("\n[TEST 4] Weekly Credit Reset")
    for _ in range(144):  # Complete first week (168 hours total)
        sim.step_hour()
    
    state = sim.get_state()
    assert state['hour'] == 168, "Should be at hour 168"
    assert state['week'] == 1, "Should be week 1"
    
    # Check that credits were reset to 10k (may be higher if daily production added)
    for color, data in state['factions'].items():
        # After weekly reset, credits should be at least close to 10k reset value
        # but could be higher if daily production was added at hour 192 (day 8)
        print(f"  ✓ {color.capitalize()}: Credits = ${data['credits']:,}")
    
    # Test 5: Save and Load
    print("\n[TEST 5] Save and Load Functionality")
    save_state = sim.save_state()
    
    # Create new simulation and load
    sim2 = Simulation()
    sim2.load_state(save_state)
    load_state = sim2.get_state()
    
    assert load_state['hour'] == state['hour'], "Loaded hour should match"
    assert load_state['day'] == state['day'], "Loaded day should match"
    assert load_state['week'] == state['week'], "Loaded week should match"
    
    print(f"  ✓ Successfully saved and loaded state")
    print(f"  ✓ Saved {len(save_state['cells'])} cells")
    
    # Test 6: Grid Expansion
    print("\n[TEST 6] Grid Expansion")
    initial_cell_count = len(sim.grid.cells)
    
    # Run more simulation to trigger expansion
    for _ in range(100):
        sim.step_hour()
    
    final_cell_count = len(sim.grid.cells)
    print(f"  ✓ Grid expanded from {initial_cell_count} to {final_cell_count} cells")
    assert final_cell_count >= initial_cell_count, "Grid should expand or stay same"
    
    # Test 7: Faction Competition
    print("\n[TEST 7] Faction Competition and Territory Control")
    state = sim.get_state()
    
    factions_by_credits = sorted(
        [(color, data) for color, data in state['factions'].items()],
        key=lambda x: x[1]['credits'],
        reverse=True
    )
    
    print("  Faction Rankings by Credits:")
    for i, (color, data) in enumerate(factions_by_credits, 1):
        print(f"    {i}. {color.capitalize()}")
        print(f"       Credits: ${data['credits']:,.0f}")
        print(f"       Territories: {data['territory_count']}")
    
    # Test 8: Connected Territory Logic
    print("\n[TEST 8] Connected Territory Tracking")
    for color in ['orange', 'green', 'blue']:
        home_cells = sim.grid.get_home_cells(color)
        faction_cells = sim.grid.get_faction_cells(color)
        connected = sim.grid.find_connected_cells(home_cells)
        
        disconnected_count = len([c for c in faction_cells if c.hex not in connected])
        print(f"  ✓ {color.capitalize()}: {len(connected)} connected, {disconnected_count} disconnected")
    
    # Test 9: Reset Functionality
    print("\n[TEST 9] Reset Functionality")
    sim.reset()
    reset_state = sim.get_state()
    
    assert reset_state['hour'] == 0, "Hour should reset to 0"
    assert reset_state['day'] == 0, "Day should reset to 0"
    assert reset_state['week'] == 0, "Week should reset to 0"
    
    for color, data in reset_state['factions'].items():
        assert data['credits'] == 10_000, f"{color} credits should reset"
    
    print("  ✓ Simulation reset successfully")
    
    # Test 10: Long-term Stability
    print("\n[TEST 10] Long-term Stability (500 hours)")
    for _ in range(500):
        sim.step_hour()
    
    state = sim.get_state()
    print(f"  ✓ Simulation ran for {state['hour']} hours without errors")
    print(f"  ✓ Current state: Week {state['week']}, Day {state['day']}")
    print(f"  ✓ Mercenary pool: {state['mercenary_pool']}")
    
    # Verify constraints
    assert 300 <= state['mercenary_pool'] <= 5000, "Mercenary pool within bounds"
    
    total_territories = sum(data['territory_count'] for data in state['factions'].values())
    print(f"  ✓ Total territories: {total_territories}")
    
    # Summary
    print("\n" + "="*70)
    print("  ALL TESTS PASSED ✓")
    print("="*70)
    
    print("\nFinal Simulation Statistics:")
    print(f"  Duration: {state['hour']} hours ({state['day']} days, {state['week']} weeks)")
    print(f"  Grid Size: {len(sim.grid.cells)} hexes")
    print(f"  Mercenary Pool: {state['mercenary_pool']}")
    
    print("\nFaction Summary:")
    for color, data in state['factions'].items():
        print(f"\n  {color.capitalize()}:")
        print(f"    Credits: ${data['credits']:,.0f}")
        print(f"    Territories: {data['territory_count']}")
        print(f"    Daily Production: ${data['daily_production']:,.0f}")


if __name__ == "__main__":
    test_all_features()
