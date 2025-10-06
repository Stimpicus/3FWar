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
    
    def to_pixel(self, size: float, origin: Tuple[float, float]) -> Tuple[float, float]:
        """Convert hex coordinates to pixel coordinates."""
        x = size * (3/2 * self.q)
        y = size * (math.sqrt(3)/2 * self.q + math.sqrt(3) * self.r)
        return (origin[0] + x, origin[1] + y)


class HexCell:
    """Represents a hex cell with game state."""
    
    def __init__(self, hex_pos: Hex, owner: Optional[str] = None, is_home: bool = False):
        self.hex = hex_pos
        self.owner = owner  # None, 'grey', 'orange', 'green', 'blue'
        self.is_home = is_home  # True for home base hexes
        self.resources = 0.0  # Accumulated resources
        self.protection_until = 0  # Simulation hour until which this cell is protected
        
    def is_protected(self, current_hour: int) -> bool:
        """Check if this cell is currently protected."""
        return current_hour < self.protection_until
    
    def set_protection(self, current_hour: int, duration: int = 3):
        """Set protection for this cell."""
        self.protection_until = current_hour + duration
    
    def produce_resources(self, base_value: float = 100.0):
        """Produce resources based on distance from center."""
        distance = self.hex.distance_from_center()
        # Resources scale with distance: closer = less valuable, farther = more valuable
        multiplier = 1 + (distance * 0.1)
        self.resources += base_value * multiplier
    
    def deposit_resources(self) -> float:
        """Deposit accumulated resources and return the amount."""
        amount = self.resources
        self.resources = 0.0
        return amount
    
    def reset(self):
        """Reset cell to unclaimed state."""
        if not self.is_home:
            self.owner = None
            self.resources = 0.0
            self.protection_until = 0


class HexGrid:
    """Manages the hex grid and all hex cells."""
    
    def __init__(self):
        self.cells = {}  # Dict[Hex, HexCell]
        self.initial_hexes = set()  # Track initial grid size
        self._initialize_grid()
    
    def _initialize_grid(self):
        """Initialize the grid with the home bases from the image."""
        # Center grey hexes
        grey_coords = [
            (0, 0), (-1, 1), (0, 1), (1, 0), (1, -1), (0, -1), (-1, 0),
            (-2, 1), (-1, 2), (1, 1), (2, 0), (2, -1), (1, -2), (-1, -1), (-2, 0),
            (-2, 2), (0, 2), (2, 1), (3, 0), (3, -1), (2, -2), (0, -2), (-2, -1), (-3, 1)
        ]
        
        # Orange hexes (top)
        orange_coords = [
            (-1, -2), (0, -3), (1, -3), (2, -3), (3, -2), (4, -2),
            (-1, -3), (0, -4), (1, -4), (2, -4), (3, -3), (4, -3),
            (0, -5), (1, -5), (2, -5), (3, -4)
        ]
        
        # Green hexes (bottom-left)
        green_coords = [
            (-3, 2), (-4, 3), (-3, 3), (-2, 3),
            (-4, 4), (-3, 4), (-2, 4), (-1, 3),
            (-5, 5), (-4, 5), (-3, 5), (-2, 5), (-1, 4)
        ]
        
        # Blue hexes (bottom-right)
        blue_coords = [
            (3, 1), (4, 1), (4, 0), (5, 0),
            (4, 2), (5, 1), (5, -1), (6, 0),
            (5, 2), (6, 1), (6, -1), (7, 0)
        ]
        
        # Yellow border hexes (unclaimed)
        yellow_coords = [
            # Top border
            (-2, -3), (-1, -4), (-2, -2), (1, -6), (2, -6), (3, -5), (4, -4), (5, -3),
            # Right border
            (5, -2), (6, -1), (7, -1), (7, 1), (6, 2), (5, 3), (4, 3),
            # Bottom-right border
            (3, 2), (2, 2), (1, 2), (0, 3), (-1, 5),
            # Bottom border
            (-2, 6), (-3, 6), (-4, 6), (-5, 6),
            # Left border
            (-5, 4), (-5, 3), (-5, 2), (-4, 2), (-4, 1), (-3, 0), (-3, -1), (-2, -2),
            # Additional yellow hexes to complete the border
            (-1, -5), (4, -5), (5, -4), (6, -2), (8, 0), (7, 2), (3, 3), (1, 3),
            (-6, 5), (-6, 4), (-6, 3), (-6, 2), (-5, 1), (-4, 0), (-3, -2),
        ]
        
        # Create cells
        for q, r in grey_coords:
            hex_pos = Hex(q, r)
            self.cells[hex_pos] = HexCell(hex_pos, 'grey', is_home=True)
            self.initial_hexes.add(hex_pos)
        
        for q, r in orange_coords:
            hex_pos = Hex(q, r)
            self.cells[hex_pos] = HexCell(hex_pos, 'orange', is_home=True)
            self.initial_hexes.add(hex_pos)
        
        for q, r in green_coords:
            hex_pos = Hex(q, r)
            self.cells[hex_pos] = HexCell(hex_pos, 'green', is_home=True)
            self.initial_hexes.add(hex_pos)
        
        for q, r in blue_coords:
            hex_pos = Hex(q, r)
            self.cells[hex_pos] = HexCell(hex_pos, 'blue', is_home=True)
            self.initial_hexes.add(hex_pos)
        
        for q, r in yellow_coords:
            hex_pos = Hex(q, r)
            self.cells[hex_pos] = HexCell(hex_pos, None, is_home=False)
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
            self.cells[hex_pos] = HexCell(hex_pos, None, is_home=False)
    
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
