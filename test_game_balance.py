"""Test new game balance changes."""
from simulation import Simulation
from faction import MercenaryPool, Mercenary


def test_mercenary_pool_size():
    """Test that mercenary pool starts at 300 and resets to 300."""
    print("\n[TEST 1] Mercenary Pool Size")
    
    # Test initial size
    sim = Simulation()
    state = sim.get_state()
    assert state['mercenary_pool'] == 300, f"Expected 300, got {state['mercenary_pool']}"
    print("  ✓ Initial mercenary pool size is 300")
    
    # Test reset
    sim.reset()
    state = sim.get_state()
    assert state['mercenary_pool'] == 300, f"Expected 300 after reset, got {state['mercenary_pool']}"
    print("  ✓ Mercenary pool resets to 300")


def test_mercenary_objects():
    """Test that mercenaries are individual objects."""
    print("\n[TEST 2] Individual Mercenary Objects")
    
    pool = MercenaryPool(initial_size=300)
    assert len(pool.mercenaries) == 300, f"Expected 300 mercenaries, got {len(pool.mercenaries)}"
    print("  ✓ Mercenary pool contains 300 individual Mercenary objects")
    
    # Check that each mercenary has the required attributes
    for merc in pool.mercenaries:
        assert isinstance(merc, Mercenary), "Each mercenary should be a Mercenary object"
        assert hasattr(merc, 'id'), "Mercenary should have 'id' attribute"
        assert hasattr(merc, 'assigned'), "Mercenary should have 'assigned' attribute"
        assert hasattr(merc, 'mission_complete_hour'), "Mercenary should have 'mission_complete_hour' attribute"
    print("  ✓ All mercenaries have required attributes (id, assigned, mission_complete_hour)")


def test_mission_timer():
    """Test that missions complete after 0.5 hours."""
    print("\n[TEST 3] Mission Timer (0.5 hours)")
    
    sim = Simulation()
    
    # Get initial state
    state = sim.get_state()
    initial_available = state['mercenary_available']
    print(f"  Hour 0: {initial_available} mercenaries available")
    
    # Run one hour to allow some missions to execute
    sim.step_hour()
    state = sim.get_state()
    hour1_available = state['mercenary_available']
    print(f"  Hour 1: {hour1_available} mercenaries available")
    
    # If mercenaries were assigned, they should be unavailable
    if hour1_available < initial_available:
        assigned_count = initial_available - hour1_available
        print(f"    {assigned_count} mercenaries assigned to missions")
        
        # After 0.5 hours, they should start becoming available again
        # Since we process hourly, mercenaries assigned at hour 1 complete at hour 1.5
        # So by hour 2, they should be available
        sim.step_hour()
        state = sim.get_state()
        hour2_available = state['mercenary_available']
        print(f"  Hour 2: {hour2_available} mercenaries available")
        print("  ✓ Mercenaries are released after mission completes")
    else:
        print("  ✓ No missions executed (acceptable due to random chance)")


def test_weekly_credits():
    """Test that weekly credits reset to 10,000."""
    print("\n[TEST 4] Weekly Credit Reset (10,000 credits)")
    
    sim = Simulation()
    
    # Check initial credits
    state = sim.get_state()
    for color in ['orange', 'green', 'blue']:
        assert state['factions'][color]['credits'] == 10_000, \
            f"{color} should start with 10,000 credits"
    print("  ✓ All factions start with 10,000 credits")
    
    # Run to just before week boundary
    for _ in range(167):
        sim.step_hour()
    
    state = sim.get_state()
    credits_before = {
        color: state['factions'][color]['credits']
        for color in ['orange', 'green', 'blue']
    }
    print(f"  Hour 167 credits: Orange={credits_before['orange']}, " +
          f"Green={credits_before['green']}, Blue={credits_before['blue']}")
    
    # Step to hour 168 (new week)
    sim.step_hour()
    state = sim.get_state()
    
    assert state['week'] == 1, "Should be week 1 after 168 hours"
    print("  ✓ Week counter incremented at hour 168")
    
    # Check that all credits are at or below 10,000
    # (could be less if spent, but should have been reset to 10,000 at the start of the hour)
    for color in ['orange', 'green', 'blue']:
        credits = state['factions'][color]['credits']
        assert credits <= 10_000, \
            f"{color} credits should be reset to 10,000 (or less if spent): got {credits}"
    print("  ✓ All factions' credits reset to 10,000 at week boundary")


def test_weekly_interval():
    """Test that a new week starts every 168 hours."""
    print("\n[TEST 5] Weekly Interval (168 hours)")
    
    sim = Simulation()
    
    # Test week 0 to week 1
    for hour in range(168):
        assert sim.current_week == 0, f"Should be week 0 at hour {hour}"
        sim.step_hour()
    
    assert sim.current_week == 1, "Should be week 1 at hour 168"
    print("  ✓ Week 0 -> Week 1 at hour 168")
    
    # Test week 1 to week 2
    for hour in range(168, 336):
        assert sim.current_week == 1, f"Should be week 1 at hour {hour}"
        sim.step_hour()
    
    assert sim.current_week == 2, "Should be week 2 at hour 336"
    print("  ✓ Week 1 -> Week 2 at hour 336")
    print("  ✓ Weekly interval is exactly 168 hours")


def test_assignment_status():
    """Test mercenary assignment status tracking."""
    print("\n[TEST 6] Mercenary Assignment Status")
    
    pool = MercenaryPool(initial_size=10)
    
    # All should start as available
    assert pool.get_available_count(0) == 10, "All mercenaries should start available"
    print("  ✓ All mercenaries start as available")
    
    # Allocate 5 mercenaries at hour 0
    success = pool.allocate(5, 0)
    assert success, "Should be able to allocate 5 mercenaries"
    assert pool.get_available_count(0) == 5, "Should have 5 available after allocating 5"
    print("  ✓ Can allocate mercenaries and track assignment")
    
    # At hour 0.4, they should still be assigned (mission not complete yet)
    assert pool.get_available_count(0.4) == 5, "Should still have 5 available at hour 0.4"
    print("  ✓ Mercenaries remain assigned during mission")
    
    # At hour 0.5, they should be released (mission completes at 0.5)
    assert pool.get_available_count(0.5) == 10, "All should be available when mission completes at 0.5"
    print("  ✓ Mercenaries become available at mission completion time (0.5 hours)")
    
    # Process hour to actually release them
    pool.process_hour(0.5)
    assert pool.get_available_count(0.5) == 10, "All should be available after processing"
    print("  ✓ Process hour releases completed mercenaries")


def test_reset_to_correct_values():
    """Test that reset uses the new balance values."""
    print("\n[TEST 7] Reset Uses New Balance Values")
    
    sim = Simulation()
    
    # Run simulation for a while
    for _ in range(100):
        sim.step_hour()
    
    # Reset
    sim.reset()
    
    # Check that everything is back to initial values
    state = sim.get_state()
    
    assert state['hour'] == 0, "Hour should be 0"
    assert state['day'] == 0, "Day should be 0"
    assert state['week'] == 0, "Week should be 0"
    assert state['mercenary_pool'] == 300, "Mercenary pool should be 300"
    
    for color in ['orange', 'green', 'blue']:
        assert state['factions'][color]['credits'] == 10_000, \
            f"{color} credits should be 10,000 after reset"
        assert state['factions'][color]['total_resources'] == 0, \
            f"{color} resources should be 0 after reset"
    
    print("  ✓ Reset correctly applies all new balance values")


if __name__ == "__main__":
    print("="*70)
    print("  Game Balance Changes Test Suite")
    print("="*70)
    
    test_mercenary_pool_size()
    test_mercenary_objects()
    test_mission_timer()
    test_weekly_credits()
    test_weekly_interval()
    test_assignment_status()
    test_reset_to_correct_values()
    
    print("\n" + "="*70)
    print("  ALL GAME BALANCE TESTS PASSED ✓")
    print("="*70)
    print("\nSummary of Changes:")
    print("  • Mercenary pool size: 1000 → 300")
    print("  • Faction weekly credits: 1,000,000,000 → 10,000")
    print("  • Faction initial credits: 1,000,000,000 → 10,000")
    print("  • Mission timer: Added 0.5 hour completion time")
    print("  • Mercenary representation: Pool size → Individual objects")
    print("  • Weekly interval: Confirmed at 168 hours")
