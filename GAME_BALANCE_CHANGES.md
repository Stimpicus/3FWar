# Game Balance Changes

This document summarizes the game balance improvements implemented for the 3FWar simulation.

## Summary of Changes

### 1. Reduced Mercenary Pool Size (1000 → 300)
- **Files Modified**: `simulation.py`, `faction.py`
- **Changes**:
  - Initial mercenary pool size reduced from 1000 to 300
  - Pool resets to 300 on simulation reset
  - Minimum pool size remains at 300, maximum at 5000

### 2. Individual Mercenary Objects with Mission Timers
- **Files Modified**: `faction.py`
- **Changes**:
  - Introduced new `Mercenary` class with:
    - `id`: unique identifier
    - `assigned`: assignment status (boolean)
    - `mission_complete_hour`: hour when mission completes
  - Refactored `MercenaryPool` to manage list of individual `Mercenary` objects
  - Added `get_available_count(current_hour)` method to check available mercenaries
  - Added `process_hour(current_hour)` method to release mercenaries after mission completion

### 3. Mission Timer (0.5 Hours)
- **Files Modified**: `faction.py`, `simulation.py`
- **Changes**:
  - Each mercenary can only accept one mission at a time
  - Missions complete 0.5 hours after assignment
  - Mercenaries automatically become available when `current_hour >= mission_complete_hour`
  - Added hourly processing in simulation to release completed mercenaries
  - Updated `allocate()` method to accept `current_hour` parameter

### 4. Reduced Base Weekly Pay (1B → 10,000 Credits)
- **Files Modified**: `faction.py`, `simulation.py`
- **Changes**:
  - Faction initial credits reduced from 1,000,000,000 to 10,000
  - Weekly credit reset reduced from 1,000,000,000 to 10,000
  - Applied to both initial state and simulation reset

### 5. Weekly Reset Confirmation (168 Hours)
- **Status**: Already implemented correctly
- **Verification**: 
  - New week starts every 168 hours (7 days × 24 hours)
  - Week counter increments at hours 168, 336, 504, etc.
  - Weekly reset triggers at these boundaries

## Technical Implementation Details

### Mercenary System
The mercenary pool was refactored from a simple counter to a collection of individual objects:

```python
class Mercenary:
    def __init__(self, merc_id: int):
        self.id = merc_id
        self.assigned = False
        self.mission_complete_hour = None
    
    def assign_mission(self, current_hour: int, duration: float = 0.5):
        self.assigned = True
        self.mission_complete_hour = current_hour + duration
    
    def is_available(self, current_hour: int) -> bool:
        if not self.assigned:
            return True
        if self.mission_complete_hour is not None and current_hour >= self.mission_complete_hour:
            return True
        return False
```

### Hourly Processing
Added mercenary processing to the simulation's `_process_hourly()` method:

```python
def _process_hourly(self):
    # 1. Process mercenary missions (release completed missions)
    self.mercenary_pool.process_hour(self.current_hour)
    
    # 2. Shrink disconnected territories
    self._shrink_disconnected_territories()
    
    # 3. Produce resources for connected territories
    self._produce_resources()
```

### Save/Load Compatibility
- Save state now includes individual mercenary data (id, assigned, mission_complete_hour)
- Load state supports both old format (pool size only) and new format (individual mercenaries)
- Backwards compatible with old save files

## Testing

### New Test Suite
Created `test_game_balance.py` with comprehensive tests:
1. Mercenary pool size verification
2. Individual mercenary object verification
3. Mission timer functionality
4. Weekly credit reset
5. Weekly interval (168 hours)
6. Mercenary assignment status tracking
7. Reset value verification

### Updated Tests
Modified `test_comprehensive.py` to reflect new credit values:
- Initial credits: 1B → 10k
- Weekly reset credits: 1B → 10k

### Test Results
All tests passing:
- ✓ test_comprehensive.py
- ✓ test_sim.py
- ✓ test_requirements.py
- ✓ test_contiguity.py
- ✓ test_contiguity_advanced.py
- ✓ test_disrupt_reclaim.py
- ✓ test_game_balance.py

## Impact on Gameplay

### Strategic Changes
1. **Resource Scarcity**: With only 300 mercenaries available (down from 1000), factions must compete more carefully for mercenary allocation
2. **Economic Pressure**: Weekly credits of 10,000 (down from 1B) creates meaningful economic constraints
3. **Mission Timing**: 0.5-hour mission timer means mercenaries are temporarily unavailable, requiring better planning
4. **Assignment Strategy**: Individual mercenary tracking allows for more sophisticated mission scheduling

### Balance Improvements
- Factions can no longer execute unlimited concurrent missions
- Credits become a meaningful limiting factor
- Mission execution requires strategic timing
- Resource production becomes more important relative to credits

## Files Changed

### Core Files
- `faction.py`: Added Mercenary class, refactored MercenaryPool, updated credit values
- `simulation.py`: Updated pool initialization, reset logic, hourly processing, save/load
- `test_comprehensive.py`: Updated credit assertions

### New Files
- `test_game_balance.py`: Comprehensive test suite for all balance changes

## Verification

All requirements from the problem statement have been implemented and verified:

✓ Mercenary pool size: 300 (initial and on reset)  
✓ Mission timer: 0.5 hours per mission  
✓ Individual mercenary objects with assignment status and timer  
✓ Base weekly pay: 10,000 credits (initial and weekly reset)  
✓ Weekly interval: 168 hours (7 days)  

The implementation maintains backward compatibility with existing save files and all existing tests continue to pass.
