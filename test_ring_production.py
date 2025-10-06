"""Test script to verify ring-based resource production."""
from hex_grid import Hex, HexCell


def test_ring_multipliers():
    """Test that the ring multiplier lookup table is correct."""
    print("Testing ring multiplier lookup table...")
    
    # Test hexes at different rings
    test_cases = [
        (Hex(0, 0), 0, 1.0),      # Ring 0 (center)
        (Hex(1, 0), 1, 1.1),      # Ring 1
        (Hex(0, 2), 2, 1.2),      # Ring 2
        (Hex(0, 3), 3, 1.3),      # Ring 3
        (Hex(0, 4), 4, 1.4),      # Ring 4
        (Hex(0, 5), 5, 1.4),      # Ring 5 (should be capped at 1.4)
        (Hex(3, -3), 3, 1.3),     # Ring 3 (different direction)
        (Hex(-4, 4), 4, 1.4),     # Ring 4 (different direction)
    ]
    
    for hex_pos, expected_ring, expected_multiplier in test_cases:
        cell = HexCell(hex_pos)
        actual_ring = hex_pos.distance_from_center()
        actual_multiplier = cell._get_ring_multiplier(actual_ring)
        
        assert actual_ring == expected_ring, \
            f"Ring mismatch for {hex_pos}: expected {expected_ring}, got {actual_ring}"
        assert actual_multiplier == expected_multiplier, \
            f"Multiplier mismatch for {hex_pos} (ring {actual_ring}): expected {expected_multiplier}, got {actual_multiplier}"
        
        print(f"  ✓ {hex_pos} -> Ring {actual_ring}, Multiplier {actual_multiplier}")
    
    print("  ✓ All ring multipliers correct!\n")


def test_resource_production_per_ring():
    """Test that resource production scales correctly per ring."""
    print("Testing resource production per ring...")
    
    base_value = 100.0
    
    # Test hexes at different rings
    test_cases = [
        (Hex(0, 0), 0, 100.0),    # Ring 0: 100 * 1.0 = 100
        (Hex(1, 0), 1, 110.0),    # Ring 1: 100 * 1.1 = 110
        (Hex(0, 2), 2, 120.0),    # Ring 2: 100 * 1.2 = 120
        (Hex(0, 3), 3, 130.0),    # Ring 3: 100 * 1.3 = 130
        (Hex(0, 4), 4, 140.0),    # Ring 4: 100 * 1.4 = 140
        (Hex(0, 5), 5, 140.0),    # Ring 5: 100 * 1.4 = 140 (capped)
    ]
    
    for hex_pos, ring, expected_production in test_cases:
        cell = HexCell(hex_pos)
        cell.produce_resources(base_value)
        
        assert abs(cell.resources - expected_production) < 0.01, \
            f"Production mismatch for {hex_pos} (ring {ring}): expected {expected_production}, got {cell.resources}"
        
        print(f"  ✓ Ring {ring} ({hex_pos}): {cell.resources:.1f} resources produced")
    
    print("  ✓ All resource production correct!\n")


def test_cumulative_production():
    """Test cumulative resource production over multiple calls."""
    print("Testing cumulative resource production...")
    
    cell = HexCell(Hex(0, 2))  # Ring 2, multiplier 1.2
    base_value = 100.0
    
    # Produce resources 3 times
    for i in range(1, 4):
        cell.produce_resources(base_value)
        expected = 120.0 * i
        assert abs(cell.resources - expected) < 0.01, \
            f"Cumulative production mismatch after {i} calls: expected {expected}, got {cell.resources}"
        print(f"  ✓ After {i} production(s): {cell.resources:.1f} resources")
    
    print("  ✓ Cumulative production correct!\n")


def test_verify_distance_calculation():
    """Verify that distance_from_center calculation is correct."""
    print("Testing distance_from_center calculation...")
    
    # Test various hexes to ensure they're in the correct rings
    test_cases = [
        # Ring 0
        (Hex(0, 0), 0),
        
        # Ring 1
        (Hex(1, 0), 1),
        (Hex(0, 1), 1),
        (Hex(-1, 1), 1),
        (Hex(-1, 0), 1),
        (Hex(0, -1), 1),
        (Hex(1, -1), 1),
        
        # Ring 2
        (Hex(2, 0), 2),
        (Hex(0, 2), 2),
        (Hex(-2, 2), 2),
        (Hex(-2, 0), 2),
        (Hex(0, -2), 2),
        (Hex(2, -2), 2),
        
        # Ring 3
        (Hex(3, 0), 3),
        (Hex(0, 3), 3),
        (Hex(-3, 3), 3),
        (Hex(-3, 0), 3),
        (Hex(0, -3), 3),
        (Hex(3, -3), 3),
        
        # Ring 4
        (Hex(4, 0), 4),
        (Hex(0, 4), 4),
        (Hex(-4, 4), 4),
        (Hex(-4, 0), 4),
        (Hex(0, -4), 4),
        (Hex(4, -4), 4),
    ]
    
    for hex_pos, expected_ring in test_cases:
        actual_ring = hex_pos.distance_from_center()
        assert actual_ring == expected_ring, \
            f"Distance mismatch for {hex_pos}: expected {expected_ring}, got {actual_ring}"
    
    print(f"  ✓ Verified {len(test_cases)} hex positions")
    print("  ✓ Distance calculation correct!\n")


if __name__ == "__main__":
    print("Running ring-based resource production tests...\n")
    test_verify_distance_calculation()
    test_ring_multipliers()
    test_resource_production_per_ring()
    test_cumulative_production()
    print("✓ All ring production tests passed!")
