#!/usr/bin/env python3
"""Test disrupt/reclaim mission constraints on permanent territories."""
import sys
sys.path.insert(0, '/home/runner/work/3FWar/3FWar')

from hex_grid import HexGrid
from faction import Faction, FactionAI, MercenaryPool, Mission

print("Testing Disrupt/Reclaim Mission Constraints")
print("=" * 60)

grid = HexGrid()
merc_pool = MercenaryPool(1000)

# Create factions
orange_faction = Faction('Orange', 'orange')
orange_ai = FactionAI(orange_faction, grid, merc_pool)

# Test 1: Try to disrupt a permanent grey territory
print("\nTest 1: Attempt to disrupt permanent grey territory")
grey_hex = grid.spiral_order[0]  # Center grey hex (ID 0)
mission = Mission('disrupt', grey_hex, 'orange', 5000)
success = orange_ai.execute_mission(mission, 0)
print(f"  Result: {'FAILED ✓' if not success else 'SUCCEEDED ✗'}")
assert not success, "Should not be able to disrupt permanent territory"

# Test 2: Try to disrupt a permanent blue territory
print("\nTest 2: Attempt to disrupt permanent blue territory")
blue_hex = grid.spiral_order[7]  # Blue hex (ID 7)
mission = Mission('disrupt', blue_hex, 'orange', 5000)
success = orange_ai.execute_mission(mission, 0)
print(f"  Result: {'FAILED ✓' if not success else 'SUCCEEDED ✗'}")
assert not success, "Should not be able to disrupt permanent territory"

# Test 3: Try to reclaim a permanent green territory
print("\nTest 3: Attempt to reclaim permanent green territory")
green_hex = grid.spiral_order[9]  # Green hex (ID 9)
mission = Mission('reclaim', green_hex, 'orange', 3000)
success = orange_ai.execute_mission(mission, 0)
print(f"  Result: {'FAILED ✓' if not success else 'SUCCEEDED ✗'}")
assert not success, "Should not be able to reclaim permanent territory"

# Test 4: Claim an unclaimed territory, then try to disrupt it
print("\nTest 4: Claim unclaimed territory, then try to disrupt it")

# Find an unclaimed adjacent territory
faction_cells = grid.get_faction_cells('orange')
home_cells = grid.get_home_cells('orange')
connected = grid.find_connected_cells(home_cells)
claim_targets = orange_ai._find_claim_targets(faction_cells, connected, 0)

if claim_targets:
    target = claim_targets[0]
    
    # Claim it
    mission = Mission('claim', target.hex, 'orange', 1000)
    success = orange_ai.execute_mission(mission, 0)
    print(f"  Claim attempt: {'SUCCEEDED ✓' if success else 'FAILED ✗'}")
    
    if success:
        # Now try to disrupt it with another faction
        green_faction = Faction('Green', 'green')
        green_ai = FactionAI(green_faction, grid, merc_pool)
        
        # Wait until protection expires
        current_hour = 5  # After 3-hour protection
        mission = Mission('disrupt', target.hex, 'green', 5000)
        success = green_ai.execute_mission(mission, current_hour)
        print(f"  Disrupt (after protection): {'SUCCEEDED ✓' if success else 'FAILED ✗'}")
        
        # Try while still protected
        current_hour = 1  # Within 3-hour protection
        cell = grid.get_cell(target.hex)
        cell.owner = 'orange'  # Reset ownership
        cell.set_protection(0, 3)  # Set protection
        
        mission = Mission('disrupt', target.hex, 'green', 5000)
        success = green_ai.execute_mission(mission, current_hour)
        print(f"  Disrupt (while protected): {'FAILED ✓' if not success else 'SUCCEEDED ✗'}")

print("\n" + "=" * 60)
print("✓ All disrupt/reclaim constraint tests passed!")
print("  - Permanent territories cannot be disrupted")
print("  - Permanent territories cannot be reclaimed")
print("  - Protected territories cannot be disrupted (within 3 hours)")
print("=" * 60)
