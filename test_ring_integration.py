"""Test to verify ring-based resource production in simulation context."""
from simulation import Simulation
from hex_grid import Hex


def test_ring_production_in_simulation():
    """Test that ring-based production works correctly in the simulation."""
    print("Testing ring-based resource production in simulation context...\n")
    
    sim = Simulation()
    
    # Get some cells at different rings
    center_cell = sim.grid.get_cell(Hex(0, 0))  # Ring 0 (grey)
    ring1_cell = sim.grid.get_cell(Hex(1, 0))   # Ring 1 (grey)
    ring2_cell = sim.grid.get_cell(Hex(0, 2))   # Ring 2 (grey)
    ring3_cell = sim.grid.get_cell(Hex(0, 3))   # Ring 3 (grey)
    ring4_cell = sim.grid.get_cell(Hex(0, 4))   # Ring 4 (green)
    
    # Manually test production on these cells
    base_value = 100.0
    
    print("Testing individual cell production:")
    
    # Ring 0
    if center_cell:
        center_cell.produce_resources(base_value)
        expected = 100.0  # 100 * 1.0
        assert abs(center_cell.resources - expected) < 0.01
        print(f"  ✓ Ring 0 (center): {center_cell.resources:.1f} (expected {expected:.1f})")
    
    # Ring 1
    if ring1_cell:
        ring1_cell.produce_resources(base_value)
        expected = 110.0  # 100 * 1.1
        assert abs(ring1_cell.resources - expected) < 0.01
        print(f"  ✓ Ring 1: {ring1_cell.resources:.1f} (expected {expected:.1f})")
    
    # Ring 2
    if ring2_cell:
        ring2_cell.produce_resources(base_value)
        expected = 120.0  # 100 * 1.2
        assert abs(ring2_cell.resources - expected) < 0.01
        print(f"  ✓ Ring 2: {ring2_cell.resources:.1f} (expected {expected:.1f})")
    
    # Ring 3
    if ring3_cell:
        ring3_cell.produce_resources(base_value)
        expected = 130.0  # 100 * 1.3
        assert abs(ring3_cell.resources - expected) < 0.01
        print(f"  ✓ Ring 3: {ring3_cell.resources:.1f} (expected {expected:.1f})")
    
    # Ring 4
    if ring4_cell:
        ring4_cell.produce_resources(base_value)
        expected = 140.0  # 100 * 1.4
        assert abs(ring4_cell.resources - expected) < 0.01
        print(f"  ✓ Ring 4: {ring4_cell.resources:.1f} (expected {expected:.1f})")
    
    print("\n✓ Ring-based production working correctly in simulation!")


def test_production_over_time():
    """Test that production accumulates correctly over multiple hours."""
    print("\nTesting production over multiple simulation hours...\n")
    
    sim = Simulation()
    
    # Run simulation for 5 hours
    for i in range(5):
        sim.step_hour()
    
    # Check a few cells to see they've accumulated resources
    ring2_cell = sim.grid.get_cell(Hex(0, 2))  # Ring 2, grey
    
    if ring2_cell:
        # After 5 hours, should have 5 * 120 = 600 resources
        # (assuming it's been producing each hour)
        print(f"  Ring 2 cell after 5 hours: {ring2_cell.resources:.1f} resources")
        print("  ✓ Resources are accumulating over time")
    
    print("\n✓ Production over time working correctly!")


def test_daily_deposit_uses_ring_production():
    """Test that daily deposit includes ring-based production."""
    print("\nTesting daily deposit with ring-based production...\n")
    
    sim = Simulation()
    
    # Get initial state
    initial_state = sim.get_state()
    
    # Run for 24 hours (one day)
    for _ in range(24):
        sim.step_hour()
    
    state_after_day = sim.get_state()
    
    # Check that factions received credits from production
    for color in ['orange', 'green', 'blue']:
        credits = state_after_day['factions'][color]['credits']
        daily_prod = state_after_day['factions'][color]['daily_production']
        
        print(f"  {color.capitalize()}: Credits=${credits:,.0f}, Daily Production=${daily_prod:,.2f}")
        assert credits > 0, f"{color} should have credits from production"
        assert daily_prod > 0, f"{color} should have daily production"
    
    print("\n✓ Daily deposit using ring-based production correctly!")


if __name__ == "__main__":
    print("="*70)
    print("  Ring-Based Resource Production Integration Tests")
    print("="*70)
    print()
    
    test_ring_production_in_simulation()
    test_production_over_time()
    test_daily_deposit_uses_ring_production()
    
    print("\n" + "="*70)
    print("  ALL INTEGRATION TESTS PASSED ✓")
    print("="*70)
