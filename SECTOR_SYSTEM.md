# Sector-Based Mission Cost System

## Overview

The sector-based mission cost system introduces native territories for each of the three playable factions (Orange, Green, and Blue). Each hex on the grid is assigned to one of these three sectors based on its axial coordinates, creating three 120-degree sectors radiating from the center.

## Sector Definitions

Sectors are defined by proximity to three main axis lines in the hexagonal coordinate system:

- **Orange Sector**: Hexes where `abs(q)` is smallest (extending along the q ≈ 0 line)
  - Primary axis: Through (0, -4) toward (0, 4)
  - Orange faction's home base: (0, -4)

- **Green Sector**: Hexes where `abs(s)` is smallest, where s = -q - r (extending along the s ≈ 0 line)
  - Primary axis: Through (-4, 4) toward (4, -4)
  - Green faction's home base: (-4, 4)

- **Blue Sector**: Hexes where `abs(r)` is smallest (extending along the r ≈ 0 line)
  - Primary axis: Through (4, 0) toward (-4, 0)
  - Blue faction's home base: (4, 0)

## Mission Cost Calculation

The mission cost calculation now includes two components:

### 1. Base Cost with Distance Scaling (Unchanged)
```
base_cost = BASE_MISSION_COST * (1 + distance_from_center * 0.05)
```

Where:
- `BASE_MISSION_COST` depends on mission type:
  - Claim: 1,000 credits
  - Disrupt: 5,000 credits
  - Reclaim: 3,000 credits

### 2. Cross-Sector Penalty (New)

When a faction sends mercenaries on a mission to a hex outside its native sector, the cost is increased based on:

#### Base Cross-Sector Multiplier
- `BASE_CROSS_SECTOR_MULTIPLIER = 1.5` (50% increase for any cross-sector operation)

#### Proximity Multiplier
The proximity multiplier increases the cost further when operating close to the native faction's home base:

```
if distance_to_native_base < PROXIMITY_DISTANCE_THRESHOLD:
    proximity_factor = 1.0 - (distance_to_native_base / PROXIMITY_DISTANCE_THRESHOLD)
    proximity_multiplier = 1.0 + proximity_factor * (MAX_PROXIMITY_MULTIPLIER - 1.0)
else:
    proximity_multiplier = 1.0
```

Where:
- `MAX_PROXIMITY_MULTIPLIER = 3.0` (3x cost when at the native base)
- `PROXIMITY_DISTANCE_THRESHOLD = 12` hexes (beyond this distance, proximity penalty is negligible)

#### Final Cost Formula
```
final_cost = base_cost * BASE_CROSS_SECTOR_MULTIPLIER * proximity_multiplier
```

## Example Costs

### Orange Faction Claiming Hexes (with claim base cost = 1000):

| Location | Sector | Distance to Native Base | Final Cost | Multiplier |
|----------|--------|------------------------|------------|------------|
| (0, -5) Orange sector | Orange | N/A | 1,250 | 1.0x |
| (-4, 5) Near Green base | Green | 1 hex | 5,312 | 4.25x |
| (-1, 8) Far from Green base | Green | 7 hexes | 1,875 | 1.5x (base cross-sector only) |
| (5, 0) Near Blue base | Blue | 1 hex | 5,312 | 4.25x |

### Disrupt Missions (with disrupt base cost = 5000):

Disrupt missions are significantly more expensive, making them economically unsuitable for permanent expansion:

- Own sector: ~6,250 credits
- Near enemy base (cross-sector): ~26,562 credits (4.25x base)
- Far from enemy base (cross-sector): ~7,000 credits (1.5x base)

## Balancing Parameters

The following parameters can be adjusted for balancing:

### In `faction.py` - `_calculate_mission_cost` method:

1. **BASE_CROSS_SECTOR_MULTIPLIER** (default: 1.5)
   - Controls the baseline penalty for operating outside native territory
   - Higher values make cross-sector expansion more expensive
   - Range: 1.0 (no penalty) to 2.0 (double cost)

2. **MAX_PROXIMITY_MULTIPLIER** (default: 3.0)
   - Controls the maximum penalty when operating at an enemy's home base
   - Higher values make disruption near enemy bases prohibitively expensive
   - Range: 1.0 (no proximity penalty) to 5.0 (extreme penalty)

3. **PROXIMITY_DISTANCE_THRESHOLD** (default: 12)
   - Distance in hexes beyond which proximity penalty becomes negligible
   - Lower values create a sharper "sphere of influence" around home bases
   - Higher values extend the penalty over a larger area
   - Range: 6 to 20 hexes

## Design Goals

This system achieves the following goals:

1. **Economic Incentives Only**: No hard restrictions prevent any faction from operating anywhere on the map

2. **Native Territory Advantage**: Factions have a natural cost advantage in their own sector

3. **Discourage Permanent Cross-Sector Expansion**: While possible, maintaining territory deep in enemy sectors is expensive

4. **Disruption Remains Viable**: High-cost disruption missions can still be used to temporarily cull enemy progress, but are too expensive for permanent occupation

5. **Balanced Expansion**: All three factions have equal-sized native sectors, creating balanced expansion opportunities

## Implementation Details

### In `hex_grid.py`:

- **HexCell.native_sector**: Stores the sector ('orange', 'green', or 'blue') for each hex
- **HexGrid._determine_native_sector()**: Calculates which sector a hex belongs to based on axial coordinates
- **HexGrid.get_faction_home_base()**: Returns the central home base hex for distance calculations

### In `faction.py`:

- **FactionAI._calculate_mission_cost()**: Updated to include cross-sector and proximity penalties

### Key Functions:

1. `Hex.distance_to(other: Hex) -> int`: Calculates hex distance between two positions
2. `HexGrid._determine_native_sector(hex_pos: Hex) -> str`: Determines sector ownership
3. `HexGrid.get_faction_home_base(faction: str) -> Optional[Hex]`: Gets faction's primary base

## Testing

Run `test_sector_system.py` to validate:
- Sector assignments are correct
- Cost multipliers work as expected
- Cross-sector penalties scale with distance
- Disrupt missions are appropriately expensive
