"""Demonstration of ring-based resource production changes."""
from hex_grid import Hex, HexCell


def demonstrate_ring_scaling():
    """Demonstrate the ring-based resource production scaling."""
    print("="*70)
    print("  Ring-Based Resource Production Demonstration")
    print("="*70)
    print()
    
    print("Resource production multipliers by ring distance from center (0, 0):")
    print()
    
    base_value = 100.0
    
    # Test all rings from 0 to 6
    for ring in range(7):
        # Create a hex at the specified ring distance
        if ring == 0:
            hex_pos = Hex(0, 0)
        else:
            # Use simple positions along the vertical axis
            hex_pos = Hex(0, ring)
        
        cell = HexCell(hex_pos)
        actual_ring = hex_pos.distance_from_center()
        multiplier = cell._get_ring_multiplier(actual_ring)
        
        # Produce resources
        cell.produce_resources(base_value)
        
        print(f"  Ring {actual_ring}: Multiplier = {multiplier:.1f}x")
        print(f"           Base Production = {base_value:.0f}")
        print(f"           Actual Production = {cell.resources:.0f}")
        print()
    
    print("="*70)
    print("  Key Points:")
    print("="*70)
    print()
    print("  • Ring 0 (center): 1.0x multiplier (base production)")
    print("  • Ring 1: 1.1x multiplier (+10%)")
    print("  • Ring 2: 1.2x multiplier (+20%)")
    print("  • Ring 3: 1.3x multiplier (+30%)")
    print("  • Ring 4+: 1.4x multiplier (+40% cap)")
    print()
    print("  Resources scale with distance from center, but cap at ring 4+")
    print("  to prevent excessive production in outer rings.")
    print()
    print("="*70)


def compare_old_vs_new():
    """Compare old linear scaling vs new lookup table scaling."""
    print("\n" + "="*70)
    print("  Comparison: Old Linear vs New Lookup Table Scaling")
    print("="*70)
    print()
    
    base_value = 100.0
    
    print(f"{'Ring':<6} {'Old Linear':<15} {'New Lookup':<15} {'Difference':<15}")
    print("-"*70)
    
    for ring in range(8):
        # Old formula: multiplier = 1 + (distance * 0.1)
        old_multiplier = 1 + (ring * 0.1)
        old_production = base_value * old_multiplier
        
        # New lookup table
        if ring == 0:
            new_multiplier = 1.0
        elif ring == 1:
            new_multiplier = 1.1
        elif ring == 2:
            new_multiplier = 1.2
        elif ring == 3:
            new_multiplier = 1.3
        else:
            new_multiplier = 1.4
        
        new_production = base_value * new_multiplier
        difference = new_production - old_production
        
        print(f"{ring:<6} {old_production:<15.1f} {new_production:<15.1f} {difference:+.1f}")
    
    print()
    print("  Note: The new system caps production at ring 4 to prevent")
    print("  excessive scaling in far outer rings while maintaining the")
    print("  same scaling for rings 0-3.")
    print()
    print("="*70)


if __name__ == "__main__":
    demonstrate_ring_scaling()
    compare_old_vs_new()
