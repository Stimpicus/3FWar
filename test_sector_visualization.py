#!/usr/bin/env python3
"""Visualize sector assignments on the grid."""
import sys
sys.path.insert(0, '/home/runner/work/3FWar/3FWar')

from hex_grid import HexGrid, Hex

grid = HexGrid()

print("=" * 70)
print("SECTOR VISUALIZATION")
print("=" * 70)

# Show a cross-section of the grid along each axis
print("\nSector assignments along the q=0 axis (Orange sector):")
print("Hex (q, r) -> sector")
for r in range(-5, 6):
    hex_pos = Hex(0, r)
    cell = grid.get_cell(hex_pos)
    if cell:
        marker = "O" if cell.owner == 'orange' else ("G" if cell.owner == 'green' else ("B" if cell.owner == 'blue' else "·"))
        print(f"  (0, {r:2d}) -> {cell.native_sector:6s} [{marker}]")
    else:
        grid.expand_grid(hex_pos)
        cell = grid.get_cell(hex_pos)
        print(f"  (0, {r:2d}) -> {cell.native_sector:6s} [·]")

print("\nSector assignments along the r=0 axis (Blue sector):")
print("Hex (q, r) -> sector")
for q in range(-5, 6):
    hex_pos = Hex(q, 0)
    cell = grid.get_cell(hex_pos)
    if cell:
        marker = "O" if cell.owner == 'orange' else ("G" if cell.owner == 'green' else ("B" if cell.owner == 'blue' else "·"))
        print(f"  ({q:2d}, 0) -> {cell.native_sector:6s} [{marker}]")
    else:
        grid.expand_grid(hex_pos)
        cell = grid.get_cell(hex_pos)
        print(f"  ({q:2d}, 0) -> {cell.native_sector:6s} [·]")

print("\nSector assignments along the s=0 axis (Green sector):")
print("Hex (q, r) -> sector (s = -q - r)")
for i in range(-5, 6):
    hex_pos = Hex(i, -i)  # s = -i - (-i) = 0
    cell = grid.get_cell(hex_pos)
    if cell:
        marker = "O" if cell.owner == 'orange' else ("G" if cell.owner == 'green' else ("B" if cell.owner == 'blue' else "·"))
        print(f"  ({i:2d}, {-i:2d}) -> {cell.native_sector:6s} [{marker}]")
    else:
        grid.expand_grid(hex_pos)
        cell = grid.get_cell(hex_pos)
        print(f"  ({i:2d}, {-i:2d}) -> {cell.native_sector:6s} [·]")

# Count distribution
all_cells = grid.get_all_cells()
orange_count = sum(1 for c in all_cells if c.native_sector == 'orange')
green_count = sum(1 for c in all_cells if c.native_sector == 'green')
blue_count = sum(1 for c in all_cells if c.native_sector == 'blue')

print(f"\nSector distribution:")
print(f"  Orange sector: {orange_count} hexes")
print(f"  Green sector: {green_count} hexes")
print(f"  Blue sector: {blue_count} hexes")
print(f"  Total: {len(all_cells)} hexes")

# Check home base alignment
print(f"\nHome base sector assignments:")
for faction in ['orange', 'green', 'blue']:
    home_cells = grid.get_home_cells(faction)
    in_sector = sum(1 for c in home_cells if c.native_sector == faction)
    print(f"  {faction.capitalize()}: {in_sector}/{len(home_cells)} home bases in {faction} sector")

print("\n" + "=" * 70)
print("Legend: O=Orange owned, G=Green owned, B=Blue owned, ·=Unclaimed")
print("=" * 70)
