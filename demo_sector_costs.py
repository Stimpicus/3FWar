#!/usr/bin/env python3
"""Demonstration of the sector-based mission reward system."""
import sys
sys.path.insert(0, '/home/runner/work/3FWar/3FWar')

from hex_grid import HexGrid, Hex
from faction import Faction, FactionAI, MercenaryPool

print("=" * 70)
print("SECTOR-BASED MISSION REWARD DEMONSTRATION")
print("=" * 70)

grid = HexGrid()
merc_pool = MercenaryPool()

# Create Orange faction AI
orange_faction = Faction('Orange', 'orange')
orange_ai = FactionAI(orange_faction, grid, merc_pool)

print("\nThe three native sectors divide the map into 120-degree regions:")
print("  • Orange Sector: Extends along q ≈ 0 (through Orange's base at (0, -4))")
print("  • Green Sector: Extends along s ≈ 0 (through Green's base at (-4, 4))")
print("  • Blue Sector: Extends along r ≈ 0 (through Blue's base at (4, 0))")

print("\n" + "-" * 70)
print("ORANGE FACTION MISSION REWARDS")
print("-" * 70)

# Define test scenarios
scenarios = [
    {
        'name': 'Claiming in own sector (baseline)',
        'hex': Hex(0, -5),
        'mission_type': 'claim'
    },
    {
        'name': 'Claiming at edge of own sector',
        'hex': Hex(1, -5),
        'mission_type': 'claim'
    },
    {
        'name': 'Claiming in Green sector (far from Green base)',
        'hex': Hex(0, 8),
        'mission_type': 'claim'
    },
    {
        'name': 'Claiming in Green sector (near Green base)',
        'hex': Hex(-3, 5),
        'mission_type': 'claim'
    },
    {
        'name': 'Claiming at Green\'s home base',
        'hex': Hex(-4, 4),
        'mission_type': 'claim'
    },
    {
        'name': 'Claiming in Blue sector (far from Blue base)',
        'hex': Hex(6, -1),
        'mission_type': 'claim'
    },
    {
        'name': 'Claiming in Blue sector (near Blue base)',
        'hex': Hex(5, 0),
        'mission_type': 'claim'
    },
]

print("\nCLAIM MISSION REWARDS (Base: 1,000 credits):")
for scenario in scenarios:
    hex_pos = scenario['hex']
    mission_type = scenario['mission_type']
    
    # Ensure the hex exists
    if hex_pos not in grid.cells:
        grid.expand_grid(hex_pos)
    
    # Calculate reward
    reward = orange_ai._calculate_mission_reward(mission_type, hex_pos)
    
    # Get sector info
    cell = grid.get_cell(hex_pos)
    sector = cell.native_sector
    
    # Calculate distances
    dist_center = hex_pos.distance_from_center()
    
    info = f"{scenario['name']:50s} | "
    info += f"Sector: {sector:6s} | "
    info += f"Cost: {reward:6,d} | "
    
    if sector != 'orange':
        native_base = grid.get_faction_home_base(sector)
        dist_to_base = hex_pos.distance_to(native_base)
        info += f"Dist to {sector} base: {dist_to_base:2d}"
    else:
        info += f"Own sector"
    
    print(f"  {info}")

print("\n" + "-" * 70)
print("DISRUPT MISSION REWARDS (Base: 5,000 credits)")
print("-" * 70)
print("\nDisruption missions are significantly more expensive, making them")
print("economically unsuitable for permanent territorial expansion:")

disrupt_scenarios = [
    ('Own sector', Hex(1, -5)),
    ('Green sector (far)', Hex(0, 8)),
    ('Green sector (near)', Hex(-3, 5)),
    ('At Green base', Hex(-4, 4)),
]

for name, hex_pos in disrupt_scenarios:
    if hex_pos not in grid.cells:
        grid.expand_grid(hex_pos)
    
    reward = orange_ai._calculate_mission_reward('disrupt', hex_pos)
    cell = grid.get_cell(hex_pos)
    sector = cell.native_sector
    
    print(f"  {name:25s}: {reward:8,d} credits (sector: {sector})")

print("\n" + "=" * 70)
print("KEY INSIGHTS")
print("=" * 70)
print("""
1. NATIVE TERRITORY ADVANTAGE
   - Operating in your own sector has minimal rewards
   - Base reward only increases slightly with distance from center

2. CROSS-SECTOR PENALTY
   - 1.5x base multiplier for any cross-sector operation
   - This makes expansion into enemy territory more expensive

3. PROXIMITY PENALTY
   - Up to 3x additional reward when operating near enemy home base
   - Penalty decreases linearly with distance (threshold: 12 hexes)
   - Makes disruption near enemy bases very expensive

4. ECONOMIC DISCOURAGEMENT vs PROHIBITION
   - No hard restrictions prevent cross-sector operations
   - Economic incentives naturally guide factions to their sectors
   - Disruption missions remain viable for tactical use
   - Long-term occupation of enemy sectors is economically inefficient

5. BALANCED EXPANSION
   - All three factions have equal-sized native sectors
   - Each faction has ~30-35% of the grid as native territory
   - Promotes balanced, sector-based expansion patterns
""")

print("=" * 70)
