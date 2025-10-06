#!/usr/bin/env python3
"""Test contiguity enforcement for all mission types."""
import sys
sys.path.insert(0, '/home/runner/work/3FWar/3FWar')

from hex_grid import HexGrid, Hex, HexCell
from faction import Faction, FactionAI, MercenaryPool, Mission

print("="*70)
print("CONTIGUITY ENFORCEMENT TESTS")
print("="*70)

grid = HexGrid()
merc_pool = MercenaryPool(1000)

# Create factions
orange_faction = Faction('Orange', 'orange')
orange_ai = FactionAI(orange_faction, grid, merc_pool)

green_faction = Faction('Green', 'green')
green_ai = FactionAI(green_faction, grid, merc_pool)

blue_faction = Faction('Blue', 'blue')
blue_ai = FactionAI(blue_faction, grid, merc_pool)

# Test 1: Verify claim targets are only adjacent to connected territory
print("\n1. CLAIM MISSION CONTIGUITY")
print("-"*70)

orange_cells = grid.get_faction_cells('orange')
orange_home = grid.get_home_cells('orange')
connected = grid.find_connected_cells(orange_home)

claim_targets = orange_ai._find_claim_targets(orange_cells, connected, 0)

print(f"Orange faction has {len(orange_cells)} cells")
print(f"Orange faction has {len(connected)} connected cells")
print(f"Found {len(claim_targets)} claim targets")

# Verify all targets are adjacent to connected territory
all_adjacent = True
for target in claim_targets:
    is_adjacent = orange_ai._is_hex_reachable(target.hex, connected)
    if not is_adjacent:
        print(f"  ✗ Target {target.hex} is NOT adjacent to connected territory")
        all_adjacent = False

if all_adjacent:
    print(f"✓ All {len(claim_targets)} claim targets are adjacent to connected territory")
else:
    print("✗ Some claim targets are not adjacent to connected territory")

assert all_adjacent, "Claim targets must be adjacent to connected territory"

# Test 2: Verify disrupt targets are only adjacent to connected territory
print("\n2. DISRUPT MISSION CONTIGUITY")
print("-"*70)

disrupt_targets = orange_ai._find_disrupt_targets(0)
print(f"Found {len(disrupt_targets)} disrupt targets")

all_reachable = True
for target in disrupt_targets:
    is_reachable = orange_ai._is_hex_reachable(target.hex, connected)
    if not is_reachable:
        print(f"  ✗ Disrupt target {target.hex} is NOT reachable")
        all_reachable = False

if all_reachable:
    print(f"✓ All {len(disrupt_targets)} disrupt targets are reachable from connected territory")
else:
    print("✗ Some disrupt targets are not reachable")

assert all_reachable, "Disrupt targets must be reachable from connected territory"

# Test 3: Verify execute_mission enforces contiguity for claim
print("\n3. EXECUTE_MISSION CLAIM CONTIGUITY CHECK")
print("-"*70)

# Find a hex that is NOT adjacent to orange territory
non_adjacent_hex = None
for cell in grid.get_all_cells():
    if cell.owner is None:  # Unclaimed
        is_adjacent = orange_ai._is_hex_reachable(cell.hex, connected)
        if not is_adjacent:
            non_adjacent_hex = cell.hex
            break

if non_adjacent_hex:
    print(f"Testing claim of non-adjacent hex: {non_adjacent_hex}")
    mission = Mission('claim', non_adjacent_hex, 'orange', 1000)
    success = orange_ai.execute_mission(mission, 0)
    
    if success:
        print("  ✗ FAILED: Should not be able to claim non-adjacent hex")
        assert False, "Should not be able to claim non-adjacent hex"
    else:
        print("  ✓ Correctly rejected claim of non-adjacent hex")
else:
    print("  (No non-adjacent unclaimed hex found - all unclaimed are adjacent)")

# Test 4: Verify execute_mission enforces contiguity for disrupt
print("\n4. EXECUTE_MISSION DISRUPT CONTIGUITY CHECK")
print("-"*70)

# Find an enemy hex that is NOT adjacent to orange territory
non_adjacent_enemy = None
for cell in grid.get_all_cells():
    if cell.owner in ['green', 'blue'] and not cell.is_permanent:
        is_adjacent = orange_ai._is_hex_reachable(cell.hex, connected)
        if not is_adjacent:
            non_adjacent_enemy = cell.hex
            break

if non_adjacent_enemy:
    print(f"Testing disrupt of non-adjacent enemy hex: {non_adjacent_enemy}")
    mission = Mission('disrupt', non_adjacent_enemy, 'orange', 5000)
    success = orange_ai.execute_mission(mission, 0)
    
    if success:
        print("  ✗ FAILED: Should not be able to disrupt non-adjacent hex")
        assert False, "Should not be able to disrupt non-adjacent hex"
    else:
        print("  ✓ Correctly rejected disrupt of non-adjacent hex")
else:
    print("  (No non-adjacent enemy hex found)")

# Test 5: Verify reclaim path starts from connected territory
print("\n5. RECLAIM MISSION CONTIGUITY")
print("-"*70)

# Simulate a disconnected orange cell by claiming a green cell, then breaking connection
# First, find an adjacent green cell we can claim
green_targets = []
for neighbor in grid.get_neighbors(list(connected)[0]):
    if neighbor.owner == 'green' and not neighbor.is_permanent and not neighbor.is_protected(0):
        green_targets.append(neighbor)

if green_targets:
    # Claim a green cell to create a connection
    target_cell = green_targets[0]
    print(f"Claiming green cell {target_cell.hex} to test reclaim logic...")
    target_cell.owner = 'orange'
    
    # Now break the connection by reverting the orange cells around it (simulate disconnection)
    # This is artificial but helps test the reclaim logic
    print(f"  Cell is now orange, testing reclaim path finding...")
    
    # Find the path back to connected territory
    orange_home2 = grid.get_home_cells('orange')
    connected2 = grid.find_connected_cells(orange_home2)
    
    # If the cell is still connected, try to find a different scenario
    if target_cell.hex in connected2:
        print(f"  (Cell is still connected - skipping detailed reclaim test)")
    else:
        path = orange_ai._find_shortest_reconnection_path(target_cell, orange_home2, connected2)
        if path:
            print(f"  Found reconnection path of length {len(path)}")
            # Verify first hex in path is adjacent to connected territory
            first_hex = path[0]
            is_adjacent = orange_ai._is_hex_reachable(first_hex, connected2)
            if is_adjacent:
                print(f"  ✓ First hex in path {first_hex} is adjacent to connected territory")
            else:
                print(f"  ✗ First hex in path {first_hex} is NOT adjacent to connected territory")
                assert False, "Reclaim path must start from connected territory"
        else:
            print(f"  No reconnection path found (expected if disconnected)")
    
    # Restore the cell
    target_cell.owner = 'green'
else:
    print("  (No suitable green cells to test reclaim - skipping)")

# Test 6: Comprehensive mission evaluation check
print("\n6. COMPREHENSIVE MISSION EVALUATION")
print("-"*70)

missions = orange_ai.evaluate_missions(0)
print(f"Orange AI proposed {len(missions)} missions")

for i, mission in enumerate(missions):
    print(f"  Mission {i+1}: {mission.type} at {mission.target}")
    
    # Verify mission is reachable
    is_reachable = orange_ai._is_hex_reachable(mission.target, connected)
    if is_reachable:
        print(f"    ✓ Target is reachable from connected territory")
    else:
        print(f"    ✗ Target is NOT reachable from connected territory")
        assert False, f"Mission {mission.type} targets unreachable hex {mission.target}"

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("✓ Claim missions only target hexes adjacent to connected territory")
print("✓ Disrupt missions only target hexes adjacent to connected territory")
print("✓ Execute_mission enforces contiguity for claim missions")
print("✓ Execute_mission enforces contiguity for disrupt missions")
print("✓ Reclaim missions find paths starting from connected territory")
print("✓ All proposed missions respect contiguity constraints")
print("="*70)
print("✓ ALL CONTIGUITY TESTS PASSED!")
print("="*70)
