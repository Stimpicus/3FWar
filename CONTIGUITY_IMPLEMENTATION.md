# Contiguity Enforcement Implementation

## Overview
This document describes the implementation of strict contiguity enforcement for mission targeting in the 3FWar simulation.

## Problem Statement
The original implementation had a gap in contiguity enforcement:
- **Claim missions**: ✓ Already enforced contiguity (only targets adjacent to connected territory)
- **Disrupt missions**: ✗ Did NOT enforce contiguity (could target any enemy hex)
- **Reclaim missions**: ✗ Partial enforcement (found paths but didn't verify first hex was reachable)

## Solution
Added strict contiguity enforcement across all mission types to ensure factions can only target hexes that are:
1. Adjacent to their currently connected territory, OR
2. Part of a contiguous path from their home base

## Changes Made

### 1. New Helper Method: `_is_hex_reachable`
**Location**: `faction.py`, FactionAI class

```python
def _is_hex_reachable(self, target_hex: Hex, connected: Set[Hex]) -> bool:
    """Check if a hex is adjacent to connected faction territory."""
```

This method checks if a target hex can be reached from the faction's connected territory by:
- Checking if the hex is already in the connected set
- Checking if the hex is adjacent to any hex in the connected set

### 2. Updated `_find_disrupt_targets`
**Location**: `faction.py`, FactionAI class

**Changes**:
- Now gets the faction's connected territory at the start
- Only returns disrupt targets that are reachable via `_is_hex_reachable`
- Filters out unreachable enemy hexes before returning targets

**Before**: Could target any enemy hex that would break supply lines
**After**: Only targets reachable enemy hexes that would break supply lines

### 3. Updated `_find_shortest_reconnection_path`
**Location**: `faction.py`, FactionAI class

**Changes**:
- Now accepts `connected` parameter (set of connected hexes)
- Updated algorithm to search from disconnected cell towards connected territory
- Reverses the path so it starts from connected territory
- Returns paths that start from a reachable hex

**Before**: Found paths but didn't ensure first hex was reachable
**After**: Returns paths starting from hexes adjacent to connected territory

### 4. Updated `evaluate_missions`
**Location**: `faction.py`, FactionAI class

**Changes**:
- Passes `connected` set to `_find_shortest_reconnection_path` for reclaim missions

### 5. Updated `execute_mission`
**Location**: `faction.py`, FactionAI class

**Changes**:
- Now computes connected territory at the start
- Added contiguity check for claim missions using `_is_hex_reachable`
- Added contiguity check for disrupt/reclaim missions using `_is_hex_reachable`

**Before**: Only checked if hex was unclaimed/enemy-owned
**After**: Also verifies hex is reachable from connected territory

## Testing

### Test Coverage
1. **test_contiguity.py**: Basic contiguity enforcement tests
   - Claim missions only target adjacent hexes
   - Disrupt missions only target reachable hexes
   - Execute_mission enforces contiguity for all mission types
   - Reclaim paths start from connected territory

2. **test_contiguity_advanced.py**: Advanced scenario tests
   - Enemy territory blocking expansion
   - Expansion maintains contiguity
   - Disrupt missions target reachable enemies
   - Non-contiguous mission rejection
   - Reclaim path finding

3. **Existing tests**: All pass without modification
   - test_requirements.py: ✓
   - test_disrupt_reclaim.py: ✓
   - test_sim.py: ✓
   - test_comprehensive.py: ✓

### Test Results
All tests pass successfully, confirming:
- ✓ Contiguity is enforced for all mission types
- ✓ Factions can only expand from connected territory
- ✓ Disrupt missions respect contiguity constraints
- ✓ Reclaim paths start from reachable hexes
- ✓ Simulation runs correctly with new constraints
- ✓ No regressions in existing functionality

## Impact on Gameplay

### Before Contiguity Enforcement
- Factions could disrupt enemy hexes anywhere on the map
- Led to unrealistic "leap-frogging" attacks
- Disconnected disruptions were possible

### After Contiguity Enforcement
- Factions must expand contiguously from their home base
- All missions (Claim, Disrupt, Reclaim) require adjacent access
- More realistic territorial warfare
- Strategic positioning becomes more important

## Performance Impact
- Minimal: Added `_is_hex_reachable` method is O(6) for neighbor checks
- `find_connected_cells` was already being called, now just used more consistently
- No noticeable performance degradation in 500+ hour simulations

## Backwards Compatibility
- No changes to save/load format
- No changes to existing data structures
- All existing tests pass without modification
- Simulation behavior is more restrictive but otherwise unchanged

## Summary
The implementation successfully enforces strict contiguity for all mission types while maintaining backwards compatibility and minimal code changes. The solution uses the existing `find_connected_cells` infrastructure and adds a simple reachability check to ensure all missions respect the contiguity constraint.
