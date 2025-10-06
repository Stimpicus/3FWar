# Dynamic Mission Reward System

This document describes the implementation of the dynamic mission reward system that replaced the faction credit cost system.

## Summary of Changes

### 1. Removed Faction Income (10,000 → 0 Credits)
- **Files Modified**: `faction.py`, `simulation.py`
- **Changes**:
  - Faction initial credits reduced from 10,000 to 0
  - Factions no longer receive initial credits
  - Weekly credit reset removed (no guaranteed income)
  - Factions now only earn credits through daily resource production

### 2. Mission Cost → Mission Reward
- **Files Modified**: `faction.py`
- **Changes**:
  - Changed `Mission` class from `cost` parameter to `reward` parameter
  - Missions now offer rewards to mercenaries instead of costing faction credits
  - Rewards are not deducted from faction credits
  - Each mission requires only 1 mercenary (no longer scaled by cost)

### 3. Dynamic Reward Calculation
- **Files Modified**: `faction.py`
- **Method**: `FactionAI._calculate_mission_reward()`
- **Base Rewards**:
  - Claim: 1,000 credits
  - Disrupt: 5,000 credits
  - Reclaim: 3,000 credits

### 4. Territory-Based Reward Scaling

The reward system implements balance mechanics based on territory distribution:

#### Claim Mission Rewards:
- **Faction with LEAST territories**:
  - Receives proportionally HIGHER rewards
  - Multiplier: 1 + (most_territories / least_territories - 1) * 0.5
  - Capped at 3x base reward
  
- **Faction with MOST territories**:
  - Receives proportionally LOWER rewards
  - Multiplier: least_territories / most_territories
  - Minimum of 0.3x base reward

#### Disrupt Mission Rewards:
- **Targeting faction with LEAST territories**:
  - Rewards are DECREASED
  - Multiplier: least_territories / most_territories (min 0.3x)
  
- **Targeting faction with MOST territories**:
  - Rewards are INCREASED
  - Multiplier: 1 + (most_territories / least_territories - 1) * 0.5 (max 3x)

#### Reclaim Mission Rewards:
- Uses same logic as Claim missions (benefits the executing faction)

## Technical Implementation

### Territory Counting
New helper methods added to `FactionAI`:

```python
def _get_territory_counts(self) -> dict:
    """Get territory counts for all factions."""
    counts = {}
    for color in ['orange', 'green', 'blue']:
        counts[color] = len(self.grid.get_faction_cells(color))
    return counts

def _get_faction_with_most_territories(self, counts: dict) -> tuple:
    """Get faction with most territories and the count."""
    max_color = max(counts, key=counts.get)
    return max_color, counts[max_color]

def _get_faction_with_least_territories(self, counts: dict) -> tuple:
    """Get faction with least territories and the count."""
    min_color = min(counts, key=counts.get)
    return min_color, counts[min_color]
```

### Mission Execution Changes

The `execute_mission()` method was simplified:

**Before**:
```python
# Check if faction can afford it
if not self.faction.spend_credits(mission.cost):
    return False

# Calculate required mercenaries
required_mercs = max(1, mission.cost // 10000)

# Check if mercenaries available
if not self.mercenary_pool.allocate(required_mercs, current_hour):
    self.faction.add_credits(mission.cost)  # Refund
    return False
```

**After**:
```python
# Check if mercenaries available (no longer check if faction can afford it)
# All mercenaries have equal chance regardless of mission reward
required_mercs = 1  # Each mission requires 1 mercenary

if not self.mercenary_pool.allocate(required_mercs, current_hour):
    return False

# Mission rewards are not deducted from faction credits
```

### Weekly Reset Changes

**Before**:
```python
def weekly_reset(self):
    """Reset weekly credits."""
    self.credits = 10_000
```

**After**:
```python
def weekly_reset(self):
    """Weekly reset - no longer resets credits."""
    pass  # Factions no longer receive weekly credits
```

## Example Reward Calculations

### Scenario 1: Balanced Territories
- Orange: 13 territories
- Green: 13 territories  
- Blue: 13 territories

**Result**: All factions get base rewards (1000 for claim, 5000 for disrupt)

### Scenario 2: Imbalanced Territories
- Orange: 5 territories (least)
- Green: 50 territories (most)
- Blue: 20 territories

**Claim Mission Rewards**:
- Orange claiming: 1000 * (1 + (50/5 - 1) * 0.5) = 1000 * 5.5 = 5500 (capped at 3000)
- Green claiming: 1000 * (5/50) = 100

**Disrupt Mission Rewards**:
- Disrupting Orange (least): 5000 * (5/50) = 500
- Disrupting Green (most): 5000 * (1 + (50/5 - 1) * 0.5) = 27500 (capped at 15000)

## Testing

### New Test Suite
Created `test_dynamic_rewards.py` with comprehensive tests:
1. No initial credits verification
2. No weekly credit reset verification
3. Mission uses reward field (not cost)
4. Dynamic rewards for underdog factions
5. Missions don't cost faction credits
6. Reset sets credits to 0
7. Reward scaling with territory imbalance

### Updated Tests
Modified existing test files:
- `test_game_balance.py`: Updated credit assertions (10,000 → 0)
- `test_comprehensive.py`: Updated credit assertions (10,000 → 0)
- `test_sector_system.py`: Marked as deprecated, updated to use reward terminology
- `demo_sector_costs.py`: Updated to use reward terminology

## Files Changed

### Core Files
- `faction.py`: 
  - Changed Mission.cost to Mission.reward
  - Replaced _calculate_mission_cost with _calculate_mission_reward
  - Added territory counting helper methods
  - Removed credit checking in execute_mission
  - Set initial credits to 0
  - Removed weekly credit reset
  
- `simulation.py`:
  - Set initial credits to 0 in reset()
  - Updated weekly reset comment

### Test Files
- `test_dynamic_rewards.py`: New comprehensive test suite
- `test_game_balance.py`: Updated credit assertions
- `test_comprehensive.py`: Updated credit assertions
- `test_sector_system.py`: Marked as deprecated
- `demo_sector_costs.py`: Updated terminology

## Impact on Gameplay

### Economic Changes
1. **No Starting Capital**: Factions must earn all credits through territory production
2. **No Safety Net**: No weekly credit reset means factions can't recover from losses automatically
3. **Territory-Driven Economy**: Credits come exclusively from controlled territory

### Strategic Changes
1. **Underdog Advantage**: Factions with fewer territories get better mission rewards
2. **Snowball Prevention**: Leading factions get reduced rewards, preventing runaway victories
3. **Dynamic Balance**: The system automatically adjusts to keep gameplay competitive
4. **Mission Selection**: Factions must consider territory balance when choosing missions

### Balance Improvements
- Self-balancing economy based on territory control
- Rewards incentivize attacking the leader
- Underdog factions can catch up more easily
- Credits no longer act as a limiting factor (mercenaries are the main constraint)
- Focus shifts from economic management to territorial strategy

## Verification

All requirements from the problem statement have been implemented and verified:

✓ Removed starting credits (0 instead of 10,000)  
✓ Removed weekly credit reset  
✓ Changed mission cost to mission reward  
✓ Rewards not deducted from faction credits  
✓ Dynamic reward calculation based on territory counts  
✓ Claim rewards increase for underdog, decrease for leader  
✓ Disrupt rewards decrease when targeting underdog  
✓ Disrupt rewards increase when targeting leader  
✓ All tests updated and passing  

The implementation creates a self-balancing economic system that promotes competitive gameplay and prevents runaway victories.
