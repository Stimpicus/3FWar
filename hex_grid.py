"""Hex grid coordinate system and hex cell management."""
import math
from typing import Set, Tuple, Optional, List


class Hex:
    """Represents a hexagonal cell on the grid using axial coordinates."""
    
    def __init__(self, q: int, r: int):
        self.q = q  # Column coordinate
        self.r = r  # Row coordinate
        
    def __eq__(self, other):
        return isinstance(other, Hex) and self.q == other.q and self.r == other.r
    
    def __hash__(self):
        return hash((self.q, self.r))
    
    def __repr__(self):
        return f"Hex({self.q}, {self.r})"
    
    def neighbors(self) -> List['Hex']:
        """Get all 6 neighboring hexes."""
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        return [Hex(self.q + dq, self.r + dr) for dq, dr in directions]
    
    def distance_from_center(self) -> int:
        """Calculate distance from the center hex (0, 0)."""
        return (abs(self.q) + abs(self.q + self.r) + abs(self.r)) // 2
    
    def distance_to(self, other: 'Hex') -> int:
        """Calculate distance to another hex."""
        return (abs(self.q - other.q) + abs(self.q + self.r - other.q - other.r) + abs(self.r - other.r)) // 2
    
    def to_pixel(self, size: float, origin: Tuple[float, float]) -> Tuple[float, float]:
        """Convert hex coordinates to pixel coordinates."""
        x = size * (3/2 * self.q)
        y = size * (math.sqrt(3)/2 * self.q + math.sqrt(3) * self.r)
        return (origin[0] + x, origin[1] + y)


class HexCell:
    """Represents a hex cell with game state."""
    
    def __init__(self, hex_pos: Hex, owner: Optional[str] = None, is_home: bool = False, is_permanent: bool = False, native_sector: Optional[str] = None):
        self.hex = hex_pos
        self.owner = owner  # None, 'grey', 'orange', 'green', 'blue'
        self.is_home = is_home  # True for home base hexes
        self.is_permanent = is_permanent  # True for permanently owned territories
        self.native_sector = native_sector  # 'orange', 'green', or 'blue' - which sector this hex naturally belongs to
        self.resources = 0.0  # Accumulated resources
        self.protection_until = 0  # Simulation hour until which this cell is protected
        
    def is_protected(self, current_hour: int) -> bool:
        """Check if this cell is currently protected."""
        return current_hour < self.protection_until
    
    def set_protection(self, current_hour: int, duration: int = 3):
        """Set protection for this cell."""
        self.protection_until = current_hour + duration
    
    def produce_resources(self, base_value: float = 100.0):
        """Produce resources based on ring distance from center."""
        ring = self.hex.distance_from_center()
        # Resources scale with ring: Ring 0: 1.0, Ring 1: 1.1, Ring 2: 1.2, Ring 3: 1.3, Ring 4+: 1.4
        multiplier = self._get_ring_multiplier(ring)
        self.resources += base_value * multiplier
    
    def _get_ring_multiplier(self, ring: int) -> float:
        """Get resource production multiplier for a given ring.
        
        Args:
            ring: The ring number (distance from center)
            
        Returns:
            Multiplier for resource production
        """
        if ring == 0:
            return 1.0
        elif ring == 1:
            return 1.1
        elif ring == 2:
            return 1.2
        elif ring == 3:
            return 1.3
        else:  # ring >= 4
            return 1.4
    
    def deposit_resources(self) -> float:
        """Deposit accumulated resources and return the amount."""
        amount = self.resources
        self.resources = 0.0
        return amount
    
    def reset(self):
        """Reset cell to unclaimed state."""
        if not self.is_home and not self.is_permanent:
            self.owner = None
            self.resources = 0.0
            self.protection_until = 0


class HexGrid:
    """Manages the hex grid and all hex cells."""
    
    def __init__(self):
        self.cells = {}  # Dict[Hex, HexCell]
        self.initial_hexes = set()  # Track initial grid size
        self.spiral_order = []  # Track spiral order of hexes
        
        # Define sector axis endpoints for native territories
        # Orange sector: extends through (4, -4) - the r-axis direction
        # Green sector: extends through (0, 4) - the negative q-axis direction  
        # Blue sector: extends through (-4, 0) - the negative s-axis (positive q+r) direction
        self.sector_axes = {
            'orange': Hex(4, -4),   # r = -4, s = 0
            'green': Hex(0, 4),     # q = 0, s = -4
            'blue': Hex(-4, 0)      # q = -4, r = 0
        }
        
        self._initialize_grid()
    
    def _generate_spiral_order(self) -> List[Hex]:
        """Generate spiral order starting from center, going downward and clockwise.
        
        Returns list of Hex positions in spiral order for IDs 0-60.
        Spiral pattern: center (0,0), then move down and spiral clockwise.
        """
        spiral = []
        
        # Start at center (ID 0)
        spiral.append(Hex(0, 0))
        
        # Spiral outward in rings
        # Ring 1 (IDs 1-6): Start below center and go clockwise
        ring1 = [
            Hex(0, 1),    # ID 1: Down from center
            Hex(-1, 1),   # ID 2: Down-left
            Hex(-1, 0),   # ID 3: Left
            Hex(0, -1),   # ID 4: Up-left
            Hex(1, -1),   # ID 5: Up
            Hex(1, 0),    # ID 6: Up-right
        ]
        spiral.extend(ring1)
        
        # Ring 2 (IDs 7-18): Continue clockwise from below center
        ring2 = [
            Hex(1, 1),    # ID 7: Down-right from center
            Hex(0, 2),    # ID 8: Down
            Hex(-1, 2),   # ID 9: Down-left
            Hex(-2, 2),   # ID 10: Down-left
            Hex(-2, 1),   # ID 11: Left
            Hex(-2, 0),   # ID 12: Left
            Hex(-1, -1),  # ID 13: Up-left
            Hex(0, -2),   # ID 14: Up-left
            Hex(1, -2),   # ID 15: Up
            Hex(2, -2),   # ID 16: Up
            Hex(2, -1),   # ID 17: Up-right
            Hex(2, 0),    # ID 18: Right
            Hex(2, 1),    # ID 19: Down-right
            Hex(1, 2),    # ID 20: Down-right (back toward start)
        ]
        spiral.extend(ring2)
        
        # Ring 3 (IDs 21-39)
        ring3 = [
            Hex(0, 3),    # ID 21: Down from ring 2
            Hex(-1, 3),   # ID 22: Down-left
            Hex(-2, 3),   # ID 23: Down-left
            Hex(-3, 3),   # ID 24: Down-left
            Hex(-3, 2),   # ID 25: Left
            Hex(-3, 1),   # ID 26: Left
            Hex(-3, 0),   # ID 27: Left
            Hex(-2, -1),  # ID 28: Up-left
            Hex(-1, -2),  # ID 29: Up-left
            Hex(0, -3),   # ID 30: Up-left
            Hex(1, -3),   # ID 31: Up
            Hex(2, -3),   # ID 32: Up
            Hex(3, -3),   # ID 33: Up
            Hex(3, -2),   # ID 34: Up-right
            Hex(3, -1),   # ID 35: Up-right
            Hex(3, 0),    # ID 36: Right
            Hex(3, 1),    # ID 37: Down-right
            Hex(3, 2),    # ID 38: Down-right
            Hex(2, 2),    # ID 39: Down-right (toward start)
        ]
        spiral.extend(ring3)
        
        # Ring 4 outer (IDs 40-60) - partial ring for remaining hexes
        ring4 = [
            Hex(1, 3),    # ID 40: Down from ring 3
            Hex(0, 4),    # ID 41: Down
            Hex(-1, 4),   # ID 42: Down-left
            Hex(-2, 4),   # ID 43: Down-left
            Hex(-3, 4),   # ID 44: Down-left
            Hex(-4, 4),   # ID 45: Down-left
            Hex(-4, 3),   # ID 46: Left
            Hex(-4, 2),   # ID 47: Left
            Hex(-4, 1),   # ID 48: Left
            Hex(-4, 0),   # ID 49: Left
            Hex(-3, -1),  # ID 50: Up-left
            Hex(-2, -2),  # ID 51: Up-left
            Hex(-1, -3),  # ID 52: Up-left
            Hex(0, -4),   # ID 53: Up-left
            Hex(1, -4),   # ID 54: Up
            Hex(2, -4),   # ID 55: Up
            Hex(3, -4),   # ID 56: Up
            Hex(4, -4),   # ID 57: Up
            Hex(4, -3),   # ID 58: Up-right
            Hex(4, -2),   # ID 59: Up-right
            Hex(4, -1),   # ID 60: Up-right
        ]
        spiral.extend(ring4)
        
        return spiral
    
    def _determine_native_sector(self, hex_pos: Hex) -> str:
        """Determine which sector a hex naturally belongs to based on axial coordinates.
        
        Sectors are defined by the three main axes extending from center:
        - Orange sector: Extends along the line where q ≈ 0 (through (0, -4) toward (4, -4))
        - Green sector: Extends along the line where s = -q - r ≈ 0 (through (-4, 4))
        - Blue sector: Extends along the line where r ≈ 0 (through (4, 0) toward (-4, 0))
        
        For hexes not on the axes, we determine the sector by which axis line
        they are closest to based on which coordinate has the smallest absolute value.
        
        Args:
            hex_pos: The hex position to check
            
        Returns:
            'orange', 'green', or 'blue' indicating the native sector
        """
        q, r = hex_pos.q, hex_pos.r
        s = -q - r
        
        # Use the coordinate with the smallest absolute value to determine sector
        # This creates three 120-degree sectors
        abs_q = abs(q)
        abs_r = abs(r)
        abs_s = abs(s)
        
        # Orange sector: where q is smallest (q ≈ 0, extending along negative r)
        # Green sector: where s is smallest (s ≈ 0, extending along the diagonal)
        # Blue sector: where r is smallest (r ≈ 0, extending along positive q)
        
        if abs_q <= abs_r and abs_q <= abs_s:
            # q is smallest in absolute value -> closest to q=0 line (orange sector)
            return 'orange'
        elif abs_s <= abs_q and abs_s <= abs_r:
            # s is smallest in absolute value -> closest to s=0 line (green sector)
            return 'green'
        else:
            # r is smallest in absolute value -> closest to r=0 line (blue sector)
            return 'blue'
    
    def _initialize_grid(self):
        """Initialize the grid with the home bases using axial coordinates."""
        # Generate spiral order for backwards compatibility
        self.spiral_order = self._generate_spiral_order()
        
        # Define ownership based on precise axial (Q,R) coordinates
        # Grey: 22 hexes
        grey_coords = [
            (0, 0), (0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0), (-2, 0), 
            (2, -2), (0, 2), (0, 3), (-3, 0), (3, -3), (3, -4), (4, -4), (4, -3), 
            (1, 3), (0, 4), (-1, 4), (-4, 1), (-4, 0), (-3, -1)
        ]
        
        # Orange: 13 hexes
        orange_coords = [
            (0, -2), (0, -3), (0, -4), (1, -2), (1, -3), (1, -4), (2, -3), (2, -4), 
            (-1, -1), (-1, -2), (-1, -3), (-2, -1), (-2, -2)
        ]
        
        # Blue: 13 hexes
        blue_coords = [
            (2, 0), (3, 0), (4, 0), (1, 1), (2, 1), (3, 1), (1, 2), (2, 2), 
            (2, -1), (3, -1), (4, -1), (3, -2), (4, -2)
        ]
        
        # Green: 13 hexes
        green_coords = [
            (-2, 2), (-3, 3), (-4, 4), (-2, 1), (-3, 2), (-4, 3), (-3, 1), (-4, 2), 
            (-1, 2), (-2, 3), (-3, 4), (-1, 3), (-2, 4)
        ]
        
        # Create cells for owned territories
        for q, r in grey_coords:
            hex_pos = Hex(q, r)
            native_sector = self._determine_native_sector(hex_pos)
            self.cells[hex_pos] = HexCell(hex_pos, 'grey', is_home=True, is_permanent=True, native_sector=native_sector)
            self.initial_hexes.add(hex_pos)
        
        for q, r in orange_coords:
            hex_pos = Hex(q, r)
            native_sector = self._determine_native_sector(hex_pos)
            self.cells[hex_pos] = HexCell(hex_pos, 'orange', is_home=True, is_permanent=True, native_sector=native_sector)
            self.initial_hexes.add(hex_pos)
        
        for q, r in blue_coords:
            hex_pos = Hex(q, r)
            native_sector = self._determine_native_sector(hex_pos)
            self.cells[hex_pos] = HexCell(hex_pos, 'blue', is_home=True, is_permanent=True, native_sector=native_sector)
            self.initial_hexes.add(hex_pos)
        
        for q, r in green_coords:
            hex_pos = Hex(q, r)
            native_sector = self._determine_native_sector(hex_pos)
            self.cells[hex_pos] = HexCell(hex_pos, 'green', is_home=True, is_permanent=True, native_sector=native_sector)
            self.initial_hexes.add(hex_pos)
        
        # Add surrounding yellow (unclaimed) border hexes
        # These are hexes directly adjacent to the owned territories
        yellow_coords = [
            (-5, 0), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-5, 5), (-4, -1), (-4, 5),
            (-3, -2), (-3, 5), (-2, -3), (-2, 5), (-1, -4), (-1, 5), (0, -5), (0, 5),
            (1, -5), (1, 4), (2, -5), (2, 3), (3, -5), (3, 2), (4, -5), (4, 1),
            (5, -5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 0),
        ]
        
        for q, r in yellow_coords:
            hex_pos = Hex(q, r)
            if hex_pos not in self.cells:  # Don't overwrite existing cells
                native_sector = self._determine_native_sector(hex_pos)
                self.cells[hex_pos] = HexCell(hex_pos, None, is_home=False, is_permanent=False, native_sector=native_sector)
                self.initial_hexes.add(hex_pos)
    
    def get_cell(self, hex_pos: Hex) -> Optional[HexCell]:
        """Get cell at hex position."""
        return self.cells.get(hex_pos)
    
    def get_neighbors(self, hex_pos: Hex) -> List[HexCell]:
        """Get neighboring cells."""
        neighbors = []
        for neighbor_hex in hex_pos.neighbors():
            cell = self.get_cell(neighbor_hex)
            if cell:
                neighbors.append(cell)
        return neighbors
    
    def expand_grid(self, hex_pos: Hex):
        """Expand grid by adding a new hex at position."""
        if hex_pos not in self.cells:
            native_sector = self._determine_native_sector(hex_pos)
            self.cells[hex_pos] = HexCell(hex_pos, None, is_home=False, native_sector=native_sector)
    
    def can_remove_hex(self, hex_pos: Hex) -> bool:
        """Check if hex can be removed (must not be initial hex and must be unclaimed with no claimed neighbors)."""
        if hex_pos in self.initial_hexes:
            return False
        
        cell = self.get_cell(hex_pos)
        if not cell or cell.owner is not None:
            return False
        
        # Check if any neighbor is claimed
        for neighbor in self.get_neighbors(hex_pos):
            if neighbor.owner is not None:
                return False
        
        return True
    
    def remove_hex(self, hex_pos: Hex):
        """Remove hex from grid."""
        if self.can_remove_hex(hex_pos):
            del self.cells[hex_pos]
    
    def get_all_cells(self) -> List[HexCell]:
        """Get all cells in the grid."""
        return list(self.cells.values())
    
    def get_faction_cells(self, faction: str) -> List[HexCell]:
        """Get all cells owned by a faction."""
        return [cell for cell in self.cells.values() if cell.owner == faction]
    
    def get_home_cells(self, faction: str) -> List[HexCell]:
        """Get home base cells for a faction."""
        return [cell for cell in self.cells.values() if cell.owner == faction and cell.is_home]
    
    def get_faction_home_base(self, faction: str) -> Optional[Hex]:
        """Get the central home base hex for a faction.
        
        Returns the home base hex closest to the faction's sector axis.
        For Orange: (0, -4) is the farthest along the r-axis
        For Green: (-4, 4) is the farthest along the s-axis  
        For Blue: (4, 0) is the farthest along the q-axis
        """
        if faction == 'orange':
            return Hex(0, -4)
        elif faction == 'green':
            return Hex(-4, 4)
        elif faction == 'blue':
            return Hex(4, 0)
        return None
    
    def find_connected_cells(self, start_cells: List[HexCell]) -> Set[Hex]:
        """Find all cells connected to start_cells via same-owner neighbors."""
        if not start_cells:
            return set()
        
        owner = start_cells[0].owner
        connected = set(cell.hex for cell in start_cells)
        frontier = list(connected)
        
        while frontier:
            current_hex = frontier.pop()
            for neighbor in self.get_neighbors(current_hex):
                if neighbor.owner == owner and neighbor.hex not in connected:
                    connected.add(neighbor.hex)
                    frontier.append(neighbor.hex)
        
        return connected
