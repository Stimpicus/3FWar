#!/usr/bin/env python
"""Example usage of the 3FWar simulation."""
from simulation import Simulation
import json


def print_separator():
    """Print a separator line."""
    print("\n" + "="*70 + "\n")


def example_basic_simulation():
    """Demonstrate basic simulation usage."""
    print("EXAMPLE 1: Basic Simulation")
    print_separator()
    
    # Create simulation
    sim = Simulation()
    
    # Check initial state
    print("Initial State:")
    state = sim.get_state()
    print(f"  Hour: {state['hour']}, Day: {state['day']}, Week: {state['week']}")
    print(f"  Mercenary Pool: {state['mercenary_pool']}")
    
    for color, data in state['factions'].items():
        print(f"  {color.capitalize()}: {data['territory_count']} territories, ${data['credits']:,} credits")
    
    # Run for 24 hours (1 day)
    print("\nRunning for 24 hours...")
    for _ in range(24):
        sim.step_hour()
    
    # Check state after 1 day
    state = sim.get_state()
    print(f"\nAfter 1 day (Hour {state['hour']}):")
    for color, data in state['factions'].items():
        print(f"  {color.capitalize()}:")
        print(f"    Territories: {data['territory_count']}")
        print(f"    Daily Production: ${data['daily_production']:,.2f}")
        print(f"    Net Worth: ${data['net_worth']:,.2f}")


def example_save_load():
    """Demonstrate save/load functionality."""
    print("EXAMPLE 2: Save and Load")
    print_separator()
    
    # Create and run simulation
    sim = Simulation()
    print("Running simulation for 48 hours...")
    for _ in range(48):
        sim.step_hour()
    
    # Save state
    print("\nSaving state...")
    state = sim.save_state()
    with open('example_save.json', 'w') as f:
        json.dump(state, f, indent=2)
    print(f"✓ Saved to example_save.json")
    print(f"  Hour: {state['current_hour']}")
    print(f"  Total cells: {len(state['cells'])}")
    
    # Create new simulation and load state
    print("\nCreating new simulation and loading state...")
    sim2 = Simulation()
    with open('example_save.json', 'r') as f:
        loaded_state = json.load(f)
    sim2.load_state(loaded_state)
    
    # Verify
    new_state = sim2.get_state()
    print(f"✓ Loaded successfully")
    print(f"  Hour: {new_state['hour']}")
    print(f"  Matches original: {new_state['hour'] == state['current_hour']}")


def example_long_run():
    """Demonstrate long simulation run."""
    print("EXAMPLE 3: One Week Simulation")
    print_separator()
    
    sim = Simulation()
    
    # Run for 1 week (168 hours)
    print("Running for 1 week (168 hours)...")
    checkpoints = [24, 72, 168]  # Day 1, Day 3, Week 1
    
    for hour in range(1, 169):
        sim.step_hour()
        
        if hour in checkpoints:
            state = sim.get_state()
            print(f"\nCheckpoint at hour {hour} (Day {state['day']}, Week {state['week']}):")
            
            for color, data in state['factions'].items():
                print(f"  {color.capitalize()}:")
                print(f"    Net Worth: ${data['net_worth']:,.0f}")
                print(f"    Territories: {data['territory_count']}")
                print(f"    Daily Production: ${data['daily_production']:,.0f}")


def example_faction_competition():
    """Show faction competition dynamics."""
    print("EXAMPLE 4: Faction Competition Tracking")
    print_separator()
    
    sim = Simulation()
    
    # Track territory changes over time
    print("Tracking territory expansion over 72 hours...")
    print(f"\n{'Hour':<6} {'Orange':<10} {'Green':<10} {'Blue':<10}")
    print("-" * 40)
    
    for hour in range(0, 73, 12):  # Every 12 hours
        if hour > 0:
            for _ in range(12):
                sim.step_hour()
        
        state = sim.get_state()
        orange_terr = state['factions']['orange']['territory_count']
        green_terr = state['factions']['green']['territory_count']
        blue_terr = state['factions']['blue']['territory_count']
        
        print(f"{hour:<6} {orange_terr:<10} {green_terr:<10} {blue_terr:<10}")
    
    # Show final standings
    print("\nFinal Standings:")
    state = sim.get_state()
    factions = [(color, data) for color, data in state['factions'].items()]
    factions.sort(key=lambda x: x[1]['net_worth'], reverse=True)
    
    for i, (color, data) in enumerate(factions, 1):
        print(f"  {i}. {color.capitalize()}")
        print(f"     Net Worth: ${data['net_worth']:,.0f}")
        print(f"     Territories: {data['territory_count']}")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("  3FWar Simulation - Usage Examples")
    print("="*70)
    
    example_basic_simulation()
    print_separator()
    
    example_save_load()
    print_separator()
    
    example_long_run()
    print_separator()
    
    example_faction_competition()
    
    print("\n" + "="*70)
    print("  All examples completed successfully!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
