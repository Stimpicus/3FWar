#!/usr/bin/env python3
"""Test to verify sector-based mission cost system."""
import sys
sys.path.insert(0, '/home/runner/work/3FWar/3FWar')

from hex_grid import HexGrid, Hex
from faction import Faction, FactionAI, MercenaryPool

print("=" * 70)
print("SECTOR-BASED MISSION COST SYSTEM TEST")
print("=" * 70)

grid = HexGrid()
merc_pool = MercenaryPool()

# Create factions
orange_faction = Faction('Orange', 'orange')
green_faction = Faction('Green', 'green')
blue_faction = Faction('Blue', 'blue')

orange_ai = FactionAI(orange_faction, grid, merc_pool)
green_ai = FactionAI(green_faction, grid, merc_pool)
blue_ai = FactionAI(blue_faction, grid, merc_pool)

print("\n1. VERIFYING SECTOR ASSIGNMENTS")
print("-" * 70)

# Check that home bases are in correct sectors
orange_home_cells = grid.get_home_cells('orange')
orange_in_sector = sum(1 for cell in orange_home_cells if cell.native_sector == 'orange')
print(f"✓ Orange home bases in orange sector: {orange_in_sector}/{len(orange_home_cells)}")

green_home_cells = grid.get_home_cells('green')
green_in_sector = sum(1 for cell in green_home_cells if cell.native_sector == 'green')
print(f"✓ Green home bases in green sector: {green_in_sector}/{len(green_home_cells)}")

blue_home_cells = grid.get_home_cells('blue')
blue_in_sector = sum(1 for cell in blue_home_cells if cell.native_sector == 'blue')
print(f"✓ Blue home bases in blue sector: {blue_in_sector}/{len(blue_home_cells)}")

print("\n2. VERIFYING FACTION HOME BASE POSITIONS")
print("-" * 70)

orange_base = grid.get_faction_home_base('orange')
green_base = grid.get_faction_home_base('green')
blue_base = grid.get_faction_home_base('blue')

print(f"Orange home base: {orange_base}")
print(f"Green home base: {green_base}")
print(f"Blue home base: {blue_base}")

print("\n3. TESTING MISSION COSTS - SAME SECTOR")
print("-" * 70)

# Test orange faction in orange sector
test_hex = Hex(1, -5)
grid.expand_grid(test_hex)
cost_same = orange_ai._calculate_mission_cost('claim', test_hex)
cell = grid.get_cell(test_hex)
print(f"Orange claiming {test_hex} (sector: {cell.native_sector}): {cost_same} credits")

print("\n4. TESTING MISSION COSTS - CROSS SECTOR (NEAR BASE)")
print("-" * 70)

# Orange faction claiming near green base
green_near = Hex(-4, 5)
grid.expand_grid(green_near)
cost_cross_near = orange_ai._calculate_mission_cost('claim', green_near)
cell_near = grid.get_cell(green_near)
dist_to_green = green_near.distance_to(green_base)
print(f"Orange claiming {green_near} (sector: {cell_near.native_sector}, dist to green base: {dist_to_green}): {cost_cross_near} credits")

# Orange faction claiming near blue base
blue_near = Hex(5, -1)
grid.expand_grid(blue_near)
cost_blue_near = orange_ai._calculate_mission_cost('claim', blue_near)
cell_blue_near = grid.get_cell(blue_near)
dist_to_blue = blue_near.distance_to(blue_base)
print(f"Orange claiming {blue_near} (sector: {cell_blue_near.native_sector}, dist to blue base: {dist_to_blue}): {cost_blue_near} credits")

print("\n5. TESTING MISSION COSTS - CROSS SECTOR (FAR FROM BASE)")
print("-" * 70)

# Orange faction claiming far from green base in green sector
green_far = Hex(-1, 8)
grid.expand_grid(green_far)
cost_cross_far = orange_ai._calculate_mission_cost('claim', green_far)
cell_far = grid.get_cell(green_far)
dist_far = green_far.distance_to(green_base)
print(f"Orange claiming {green_far} (sector: {cell_far.native_sector}, dist to green base: {dist_far}): {cost_cross_far} credits")

print("\n6. TESTING DISRUPT MISSION COSTS")
print("-" * 70)

# Disrupt missions should be very expensive in cross-sector near base
disrupt_cost_near = orange_ai._calculate_mission_cost('disrupt', green_near)
disrupt_cost_far = orange_ai._calculate_mission_cost('disrupt', green_far)
disrupt_cost_same = orange_ai._calculate_mission_cost('disrupt', test_hex)

print(f"Disrupt in own sector: {disrupt_cost_same} credits")
print(f"Disrupt near enemy base (cross-sector): {disrupt_cost_near} credits")
print(f"Disrupt far from enemy base (cross-sector): {disrupt_cost_far} credits")

print("\n7. COST MULTIPLIER ANALYSIS")
print("-" * 70)

base_cost = orange_ai._calculate_mission_cost('claim', Hex(0, -4))  # Orange base
print(f"Baseline cost (at orange base): {base_cost} credits")

multipliers = []
for distance in range(0, 13):
    # Create test hex at varying distances from green base in green sector
    test_pos = Hex(-4 + distance, 4)
    grid.expand_grid(test_pos)
    cost = orange_ai._calculate_mission_cost('claim', test_pos)
    cell_test = grid.get_cell(test_pos)
    
    if cell_test.native_sector == 'green':
        multiplier = cost / base_cost if base_cost > 0 else 1.0
        actual_dist = test_pos.distance_to(green_base)
        print(f"Distance {actual_dist:2d} from green base: {cost:5d} credits ({multiplier:.2f}x)")

print("\n" + "=" * 70)
print("✓ ALL SECTOR SYSTEM TESTS COMPLETED")
print("=" * 70)
