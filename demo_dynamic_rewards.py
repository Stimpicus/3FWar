#!/usr/bin/env python3
"""Demonstration of dynamic mission reward scaling based on territory balance."""
import sys
sys.path.insert(0, '/home/runner/work/3FWar/3FWar')

from hex_grid import HexGrid, Hex
from faction import Faction, FactionAI, MercenaryPool

print("=" * 70)
print("DYNAMIC MISSION REWARD SYSTEM DEMONSTRATION")
print("=" * 70)

grid = HexGrid()
merc_pool = MercenaryPool()

# Create factions
orange_faction = Faction('Orange', 'orange')
green_faction = Faction('Green', 'green')
blue_faction = Faction('Blue', 'blue')

# Create AIs
orange_ai = FactionAI(orange_faction, grid, merc_pool)
green_ai = FactionAI(green_faction, grid, merc_pool)
blue_ai = FactionAI(blue_faction, grid, merc_pool)

print("\n1. INITIAL TERRITORY DISTRIBUTION")
print("-" * 70)

# Get territory counts
territory_counts = orange_ai._get_territory_counts()
print(f"Orange territories: {territory_counts['orange']}")
print(f"Green territories: {territory_counts['green']}")
print(f"Blue territories: {territory_counts['blue']}")

faction_with_most, most_count = orange_ai._get_faction_with_most_territories(territory_counts)
faction_with_least, least_count = orange_ai._get_faction_with_least_territories(territory_counts)

print(f"\nFaction with most territories: {faction_with_most.upper()} ({most_count})")
print(f"Faction with least territories: {faction_with_least.upper()} ({least_count})")

print("\n2. BASE MISSION REWARDS")
print("-" * 70)
print("Claim mission base reward: 1,000 credits")
print("Disrupt mission base reward: 5,000 credits")
print("Reclaim mission base reward: 3,000 credits")

print("\n3. CLAIM MISSION REWARD EXAMPLES")
print("-" * 70)

# Find a claimable hex for each faction
for color in ['orange', 'green', 'blue']:
    faction_cells = grid.get_faction_cells(color)
    ai = orange_ai if color == 'orange' else (green_ai if color == 'green' else blue_ai)
    
    if faction_cells:
        # Find an adjacent unclaimed hex
        target_hex = None
        for cell in faction_cells:
            for neighbor in grid.get_neighbors(cell.hex):
                if neighbor.owner is None:
                    target_hex = neighbor.hex
                    break
            if target_hex:
                break
        
        if target_hex:
            reward = ai._calculate_mission_reward('claim', target_hex)
            status = ""
            if color == faction_with_least and color != faction_with_most:
                status = " (UNDERDOG - HIGHER REWARD)"
            elif color == faction_with_most and color != faction_with_least:
                status = " (LEADER - LOWER REWARD)"
            
            print(f"{color.capitalize()} claiming {target_hex}: {reward:,} credits{status}")

print("\n4. DISRUPT MISSION REWARD EXAMPLES")
print("-" * 70)

# For each faction, calculate reward for disrupting others
for attacker_color in ['orange', 'green', 'blue']:
    attacker_ai = orange_ai if attacker_color == 'orange' else (green_ai if attacker_color == 'green' else blue_ai)
    
    for target_color in ['orange', 'green', 'blue']:
        if target_color == attacker_color:
            continue
        
        # Find a target cell
        target_cells = grid.get_faction_cells(target_color)
        if target_cells:
            target_cell = target_cells[0]
            reward = attacker_ai._calculate_mission_reward('disrupt', target_cell.hex)
            
            status = ""
            if target_color == faction_with_least and target_color != faction_with_most:
                status = " (targeting underdog - LOWER reward)"
            elif target_color == faction_with_most and target_color != faction_with_least:
                status = " (targeting leader - HIGHER reward)"
            
            print(f"{attacker_color.capitalize()} disrupting {target_color.capitalize()}: {reward:,} credits{status}")

print("\n5. REWARD SCALING MECHANICS")
print("-" * 70)
print("""
The reward system implements self-balancing mechanics:

CLAIM MISSIONS:
• Faction with LEAST territories → HIGHER rewards (up to 3x)
  Formula: 1 + (most/least - 1) * 0.5, capped at 3x
  
• Faction with MOST territories → LOWER rewards (down to 0.3x)
  Formula: least/most, minimum 0.3x

DISRUPT MISSIONS:
• Targeting faction with LEAST territories → LOWER rewards (down to 0.3x)
  (discourages attacking the underdog)
  
• Targeting faction with MOST territories → HIGHER rewards (up to 3x)
  (encourages attacking the leader)

This creates a self-balancing system that:
✓ Helps underdogs catch up
✓ Prevents runaway victories
✓ Encourages attacking the leader
✓ Discourages ganging up on the weakest faction
""")

print("\n6. COMPARISON WITH OLD SYSTEM")
print("-" * 70)
print("""
OLD SYSTEM (Cost-based):
• Missions COST factions credits
• Costs based on distance and sector proximity
• Factions received guaranteed weekly income (10,000 credits)
• Economic constraints limited mission execution

NEW SYSTEM (Reward-based):
• Missions REWARD mercenaries (not deducted from factions)
• Rewards based on territory balance
• No guaranteed income - credits only from production
• Territory balance determines reward scaling
• Self-balancing competitive mechanics
""")

print("=" * 70)
print("END OF DEMONSTRATION")
print("=" * 70)
