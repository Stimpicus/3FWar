# Coordinate-Based Grid Initialization Update

This document describes the changes made to replace spiral ID-based grid initialization with direct axial coordinate mapping.

## Summary of Changes

The grid initialization has been completely rewritten to use precise axial (Q,R) coordinates instead of spiral IDs. This provides a more direct and maintainable approach to defining faction territories.

## Modified Implementation

### hex_grid.py - `_initialize_grid()` method

**Previous Implementation:**
- Used `_generate_spiral_order()` to create a list of 61 hex positions in spiral order
- Assigned ownership based on spiral index IDs (0-60)
- Required mapping from spiral IDs to ownership

**New Implementation:**
- Defines exact (Q,R) coordinate lists for each faction
- Creates cells directly from coordinate lists
- Spiral order generation still exists for backwards compatibility but is NOT used for initialization

### Coordinate Assignments

The new implementation uses the following precise axial coordinates:

**Grey (22 hexes):**
```
(0,0), (0,-1), (1,-1), (1,0), (0,1), (-1,1), (-1,0), (-2,0), 
(2,-2), (0,2), (0,3), (-3,0), (3,-3), (3,-4), (4,-4), (4,-3), 
(1,3), (0,4), (-1,4), (-4,1), (-4,0), (-3,-1)
```

**Orange (13 hexes):**
```
(0,-2), (0,-3), (0,-4), (1,-2), (1,-3), (1,-4), (2,-3), (2,-4), 
(-1,-1), (-1,-2), (-1,-3), (-2,-1), (-2,-2)
```

**Blue (13 hexes):**
```
(2,0), (3,0), (4,0), (1,1), (2,1), (3,1), (1,2), (2,2), 
(2,-1), (3,-1), (4,-1), (3,-2), (4,-2)
```

**Green (13 hexes):**
```
(-2,2), (-3,3), (-4,4), (-2,1), (-3,2), (-4,3), (-3,1), (-4,2), 
(-1,2), (-2,3), (-3,4), (-1,3), (-2,4)
```

## Benefits of Coordinate-Based Approach

1. **Direct Mapping**: No intermediate spiral ID translation needed
2. **Clearer Intent**: Coordinates directly specify hex positions
3. **Easier Verification**: Can directly check if a coordinate is owned
4. **More Maintainable**: Changes to territory don't require recalculating spiral order
5. **Better Documentation**: Coordinate lists are self-documenting

## Backwards Compatibility

- The `spiral_order` attribute is still generated for backwards compatibility
- Any code that depends on `spiral_order` will continue to work
- However, the spiral order is no longer used for grid initialization

## Testing

All existing tests pass with the new implementation:

- ✅ `test_requirements.py` - Updated to verify coordinate-based mapping
- ✅ `test_coordinate_mapping.py` - New comprehensive coordinate verification test
- ✅ `test_disrupt_reclaim.py` - Permanent territory protection works correctly
- ✅ `test_contiguity.py` - Adjacency constraints working properly
- ✅ `test_sim.py` - Simulation runs correctly with new grid

## Visual Verification

Screenshot `initial_grid_coordinate_mapping.png` shows the initial grid state with:
- All 61 permanent territories correctly assigned
- Grey: 22 hexes
- Orange: 13 hexes
- Blue: 13 hexes
- Green: 13 hexes
- Proper color coding and visual indicators

## Implementation Details

The new `_initialize_grid()` method:
1. Generates spiral order for backwards compatibility
2. Defines coordinate lists for each faction
3. Creates cells directly from coordinates with proper flags:
   - `is_home=True`
   - `is_permanent=True`
4. Adds surrounding unclaimed yellow hexes
5. No dependency on spiral IDs for ownership assignment

This change fulfills the requirement to "Remove all spiral ID logic for home base assignment" while maintaining full backwards compatibility with existing code.
