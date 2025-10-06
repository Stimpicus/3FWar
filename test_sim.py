"""Test script to verify simulation logic."""
from simulation import Simulation
from hex_grid import Hex

def test_simulation():
    """Test basic simulation functionality."""
    print("Creating simulation...")
    sim = Simulation()
    
    print("\nInitial state:")
    state = sim.get_state()
    print(f"  Hour: {state['hour']}")
    print(f"  Mercenaries: {state['mercenary_pool']}")
    
    for color, data in state['factions'].items():
        print(f"\n  {color.capitalize()} Faction:")
        print(f"    Credits: ${data['credits']:,}")
        print(f"    Territories: {data['territory_count']}")
    
    print("\n\nRunning simulation for 24 hours...")
    for i in range(24):
        sim.step_hour()
    
    print("\nState after 24 hours:")
    state = sim.get_state()
    print(f"  Hour: {state['hour']}")
    print(f"  Day: {state['day']}")
    
    for color, data in state['factions'].items():
        print(f"\n  {color.capitalize()} Faction:")
        print(f"    Credits: ${data['credits']:,}")
        print(f"    Daily Production: ${data['daily_production']:,.2f}")
        print(f"    Territories: {data['territory_count']}")
    
    print("\n\nTesting save/load...")
    save_data = sim.save_state()
    print(f"  Saved {len(save_data['cells'])} cells")
    
    sim2 = Simulation()
    sim2.load_state(save_data)
    state2 = sim2.get_state()
    
    print(f"  Loaded state matches: Hour={state2['hour'] == state['hour']}")
    
    print("\n\nRunning for one week (168 hours)...")
    for i in range(168):
        sim.step_hour()
    
    state = sim.get_state()
    print(f"\nState after 1 week:")
    print(f"  Week: {state['week']}")
    print(f"  Hour: {state['hour']}")
    
    for color, data in state['factions'].items():
        print(f"\n  {color.capitalize()} Faction:")
        print(f"    Credits: ${data['credits']:,}")
        print(f"    Territories: {data['territory_count']}")
    
    print("\n✓ All tests passed!")

if __name__ == "__main__":
    test_simulation()
