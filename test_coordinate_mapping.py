#!/usr/bin/env python3
"""Test to verify coordinate-based grid initialization."""
import sys
sys.path.insert(0, '/home/runner/work/3FWar/3FWar')

from hex_grid import HexGrid, Hex

print("=" * 70)
print("COORDINATE-BASED GRID INITIALIZATION TEST")
print("=" * 70)

grid = HexGrid()

# Define expected coordinates for each faction
grey_coords = [
    (0, 0), (0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0), (-2, 0), 
    (2, -2), (0, 2), (0, 3), (-3, 0), (3, -3), (3, -4), (4, -4), (4, -3), 
    (1, 3), (0, 4), (-1, 4), (-4, 1), (-4, 0), (-3, -1)
]

orange_coords = [
    (0, -2), (0, -3), (0, -4), (1, -2), (1, -3), (1, -4), (2, -3), (2, -4), 
    (-1, -1), (-1, -2), (-1, -3), (-2, -1), (-2, -2)
]

blue_coords = [
    (2, 0), (3, 0), (4, 0), (1, 1), (2, 1), (3, 1), (1, 2), (2, 2), 
    (2, -1), (3, -1), (4, -1), (3, -2), (4, -2)
]

green_coords = [
    (-2, 2), (-3, 3), (-4, 4), (-2, 1), (-3, 2), (-4, 3), (-3, 1), (-4, 2), 
    (-1, 2), (-2, 3), (-3, 4), (-1, 3), (-2, 4)
]

print("\n1. VERIFYING COORDINATE-BASED OWNERSHIP")
print("-" * 70)

# Verify Grey coordinates
grey_errors = []
for q, r in grey_coords:
    hex_pos = Hex(q, r)
    cell = grid.get_cell(hex_pos)
    if not cell:
        grey_errors.append(f"Missing cell at ({q}, {r})")
    elif cell.owner != 'grey':
        grey_errors.append(f"Cell at ({q}, {r}) has owner '{cell.owner}' instead of 'grey'")
    elif not cell.is_permanent:
        grey_errors.append(f"Cell at ({q}, {r}) is not permanent")

if grey_errors:
    print(f"✗ Grey territory errors: {len(grey_errors)}")
    for error in grey_errors[:5]:  # Show first 5 errors
        print(f"  - {error}")
else:
    print(f"✓ All {len(grey_coords)} Grey coordinates verified")

# Verify Orange coordinates
orange_errors = []
for q, r in orange_coords:
    hex_pos = Hex(q, r)
    cell = grid.get_cell(hex_pos)
    if not cell:
        orange_errors.append(f"Missing cell at ({q}, {r})")
    elif cell.owner != 'orange':
        orange_errors.append(f"Cell at ({q}, {r}) has owner '{cell.owner}' instead of 'orange'")
    elif not cell.is_permanent:
        orange_errors.append(f"Cell at ({q}, {r}) is not permanent")

if orange_errors:
    print(f"✗ Orange territory errors: {len(orange_errors)}")
    for error in orange_errors[:5]:
        print(f"  - {error}")
else:
    print(f"✓ All {len(orange_coords)} Orange coordinates verified")

# Verify Blue coordinates
blue_errors = []
for q, r in blue_coords:
    hex_pos = Hex(q, r)
    cell = grid.get_cell(hex_pos)
    if not cell:
        blue_errors.append(f"Missing cell at ({q}, {r})")
    elif cell.owner != 'blue':
        blue_errors.append(f"Cell at ({q}, {r}) has owner '{cell.owner}' instead of 'blue'")
    elif not cell.is_permanent:
        blue_errors.append(f"Cell at ({q}, {r}) is not permanent")

if blue_errors:
    print(f"✗ Blue territory errors: {len(blue_errors)}")
    for error in blue_errors[:5]:
        print(f"  - {error}")
else:
    print(f"✓ All {len(blue_coords)} Blue coordinates verified")

# Verify Green coordinates
green_errors = []
for q, r in green_coords:
    hex_pos = Hex(q, r)
    cell = grid.get_cell(hex_pos)
    if not cell:
        green_errors.append(f"Missing cell at ({q}, {r})")
    elif cell.owner != 'green':
        green_errors.append(f"Cell at ({q}, {r}) has owner '{cell.owner}' instead of 'green'")
    elif not cell.is_permanent:
        green_errors.append(f"Cell at ({q}, {r}) is not permanent")

if green_errors:
    print(f"✗ Green territory errors: {len(green_errors)}")
    for error in green_errors[:5]:
        print(f"  - {error}")
else:
    print(f"✓ All {len(green_coords)} Green coordinates verified")

print("\n2. VERIFYING FACTION COUNTS")
print("-" * 70)

grey_count = sum(1 for c in grid.cells.values() if c.owner == 'grey' and c.is_permanent)
orange_count = sum(1 for c in grid.cells.values() if c.owner == 'orange' and c.is_permanent)
blue_count = sum(1 for c in grid.cells.values() if c.owner == 'blue' and c.is_permanent)
green_count = sum(1 for c in grid.cells.values() if c.owner == 'green' and c.is_permanent)

print(f"Grey: {grey_count}/22 {'✓' if grey_count == 22 else '✗'}")
print(f"Orange: {orange_count}/13 {'✓' if orange_count == 13 else '✗'}")
print(f"Blue: {blue_count}/13 {'✓' if blue_count == 13 else '✗'}")
print(f"Green: {green_count}/13 {'✓' if green_count == 13 else '✗'}")

total_permanent = grey_count + orange_count + blue_count + green_count
print(f"\nTotal permanent territories: {total_permanent}/61 {'✓' if total_permanent == 61 else '✗'}")

print("\n3. VERIFYING NO DUPLICATE COORDINATES")
print("-" * 70)

all_coords = grey_coords + orange_coords + blue_coords + green_coords
if len(all_coords) == len(set(all_coords)):
    print(f"✓ No duplicate coordinates found ({len(all_coords)} unique coordinates)")
else:
    print(f"✗ Duplicate coordinates detected!")
    from collections import Counter
    coord_counts = Counter(all_coords)
    duplicates = {coord: count for coord, count in coord_counts.items() if count > 1}
    print(f"  Duplicates: {duplicates}")

print("\n" + "=" * 70)
if (grey_errors == [] and orange_errors == [] and blue_errors == [] and green_errors == [] and
    grey_count == 22 and orange_count == 13 and blue_count == 13 and green_count == 13):
    print("✓ ALL TESTS PASSED - Coordinate-based mapping is correct!")
else:
    print("✗ SOME TESTS FAILED - Please review errors above")
print("=" * 70)
