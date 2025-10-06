"""Faction AI and mission management."""
import random
from typing import List, Optional, Set, Dict
from hex_grid import Hex, HexCell, HexGrid


class Mission:
    """Represents a mission offered by a faction."""
    
    def __init__(self, mission_type: str, target_hex: Hex, faction: str, cost: int):
        self.type = mission_type  # 'claim', 'disrupt', 'reclaim'
        self.target = target_hex
        self.faction = faction
        self.cost = cost
        

class Faction:
    """Represents a faction in the simulation."""
    
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color
        self.credits = 10_000  # Start with 10,000 credits
        self.daily_production = 0.0
    
    def add_credits(self, amount: float):
        """Add credits to faction."""
        self.credits += amount
    
    def spend_credits(self, amount: float) -> bool:
        """Spend credits if available."""
        if self.credits >= amount:
            self.credits -= amount
            return True
        return False
    
    def weekly_reset(self):
        """Reset weekly credits."""
        self.credits = 10_000


class Mercenary:
    """Represents an individual mercenary."""
    
    def __init__(self, merc_id: int):
        self.id = merc_id
        self.assigned = False
        self.mission_complete_hour = None  # Hour when mission completes
    
    def assign_mission(self, current_hour: int, duration: float = 0.5):
        """Assign mercenary to a mission."""
        self.assigned = True
        self.mission_complete_hour = current_hour + duration
    
    def is_available(self, current_hour: int) -> bool:
        """Check if mercenary is available."""
        if not self.assigned:
            return True
        if self.mission_complete_hour is not None and current_hour >= self.mission_complete_hour:
            return True
        return False
    
    def release(self):
        """Release mercenary from mission."""
        self.assigned = False
        self.mission_complete_hour = None


class MercenaryPool:
    """Manages the shared mercenary pool."""
    
    def __init__(self, initial_size: int = 300):
        self.mercenaries = [Mercenary(i) for i in range(initial_size)]
        self.min_size = 300
        self.max_size = 5000
    
    @property
    def size(self) -> int:
        """Return total number of mercenaries."""
        return len(self.mercenaries)
    
    @size.setter
    def size(self, value: int):
        """Set total number of mercenaries (for backwards compatibility)."""
        current = len(self.mercenaries)
        if value > current:
            # Add mercenaries
            for i in range(current, value):
                self.mercenaries.append(Mercenary(i))
        elif value < current:
            # Remove mercenaries (only remove available ones)
            to_remove = current - value
            removed = 0
            for merc in list(self.mercenaries):
                if not merc.assigned and removed < to_remove:
                    self.mercenaries.remove(merc)
                    removed += 1
    
    def get_available_count(self, current_hour: int) -> int:
        """Get count of available mercenaries."""
        return sum(1 for m in self.mercenaries if m.is_available(current_hour))
    
    def allocate(self, count: int, current_hour: int) -> bool:
        """Allocate mercenaries for a mission."""
        available = [m for m in self.mercenaries if m.is_available(current_hour)]
        if len(available) >= count:
            for i in range(count):
                available[i].assign_mission(current_hour)
            return True
        return False
    
    def release(self, count: int):
        """Release mercenaries back to pool (backwards compatibility)."""
        # This is now handled automatically by checking mission_complete_hour
        pass
    
    def process_hour(self, current_hour: int):
        """Process hourly updates - release mercenaries whose missions are complete."""
        for merc in self.mercenaries:
            if merc.assigned and merc.mission_complete_hour is not None:
                if current_hour >= merc.mission_complete_hour:
                    merc.release()
    
    def adjust_size(self, delta: int):
        """Adjust pool size within bounds."""
        new_size = max(self.min_size, min(self.max_size, len(self.mercenaries) + delta))
        self.size = new_size


class FactionAI:
    """AI logic for faction decision making."""
    
    def __init__(self, faction: Faction, grid: HexGrid, mercenary_pool: MercenaryPool):
        self.faction = faction
        self.grid = grid
        self.mercenary_pool = mercenary_pool
    
    def evaluate_missions(self, current_hour: int) -> List[Mission]:
        """Evaluate and propose missions for this faction."""
        missions = []
        
        # Get faction cells
        faction_cells = self.grid.get_faction_cells(self.faction.color)
        home_cells = self.grid.get_home_cells(self.faction.color)
        
        if not faction_cells:
            return missions
        
        # Find connected cells
        connected = self.grid.find_connected_cells(home_cells)
        
        # 1. Prioritize reclaim missions for disconnected territories
        disconnected = [cell for cell in faction_cells if cell.hex not in connected and not cell.is_home]
        if disconnected:
            for cell in disconnected[:3]:  # Limit to 3 reclaim missions
                path = self._find_shortest_reconnection_path(cell, home_cells, connected)
                if path:
                    target = path[0]  # First hex to reclaim
                    cost = self._calculate_mission_cost('reclaim', target)
                    missions.append(Mission('reclaim', target, self.faction.color, cost))
        
        # 2. Claim adjacent unclaimed hexes
        claim_targets = self._find_claim_targets(faction_cells, connected, current_hour)
        for target in claim_targets[:5]:  # Limit to 5 claim missions
            cost = self._calculate_mission_cost('claim', target.hex)
            missions.append(Mission('claim', target.hex, self.faction.color, cost))
        
        # 3. Disrupt enemy supply lines
        disrupt_targets = self._find_disrupt_targets(current_hour)
        for target in disrupt_targets[:2]:  # Limit to 2 disrupt missions
            cost = self._calculate_mission_cost('disrupt', target.hex)
            missions.append(Mission('disrupt', target.hex, self.faction.color, cost))
        
        return missions
    
    def _is_hex_reachable(self, target_hex: Hex, connected: Set[Hex]) -> bool:
        """Check if a hex is adjacent to connected faction territory.
        
        Args:
            target_hex: The hex to check
            connected: Set of hexes that are connected to home base
            
        Returns:
            True if the hex is adjacent to (or within) connected territory
        """
        # Check if target is already in connected territory
        if target_hex in connected:
            return True
        
        # Check if target is adjacent to connected territory
        for neighbor in self.grid.get_neighbors(target_hex):
            if neighbor.hex in connected:
                return True
        
        return False
    
    def _find_claim_targets(self, faction_cells: List[HexCell], connected: Set[Hex], current_hour: int) -> List[HexCell]:
        """Find unclaimed hexes adjacent to connected faction territory."""
        targets = []
        seen = set()  # Track seen hexes to avoid duplicates
        
        for cell in faction_cells:
            if cell.hex not in connected:
                continue  # Only expand from connected territory
            
            for neighbor in self.grid.get_neighbors(cell.hex):
                # Only claim unclaimed hexes (owner is None)
                # and only if they're adjacent to owned/claimed territory
                if neighbor.owner is None and neighbor.hex not in seen:
                    targets.append(neighbor)
                    seen.add(neighbor.hex)
        
        # Sort by distance from center (prioritize closer hexes for efficiency)
        targets.sort(key=lambda c: c.hex.distance_from_center())
        return targets
    
    def _find_disrupt_targets(self, current_hour: int) -> List[HexCell]:
        """Find enemy cells that would break supply lines if claimed.
        
        Only returns targets that are adjacent to connected faction territory.
        """
        targets = []
        other_factions = ['orange', 'green', 'blue']
        other_factions.remove(self.faction.color)
        
        # Get our connected territory
        home_cells = self.grid.get_home_cells(self.faction.color)
        connected = self.grid.find_connected_cells(home_cells)
        
        for enemy_color in other_factions:
            enemy_cells = self.grid.get_faction_cells(enemy_color)
            enemy_home = self.grid.get_home_cells(enemy_color)
            
            if not enemy_home:
                continue
            
            # Find cells that are critical connection points AND reachable
            for cell in enemy_cells:
                if cell.is_home or cell.is_protected(current_hour):
                    continue
                
                # Check if this cell is reachable from our connected territory
                if not self._is_hex_reachable(cell.hex, connected):
                    continue
                
                # Check if removing this cell would disconnect territory
                if self._would_disconnect(cell, enemy_home, enemy_color):
                    targets.append(cell)
        
        return targets[:5]  # Limit targets
    
    def _would_disconnect(self, cell: HexCell, home_cells: List[HexCell], faction_color: str) -> bool:
        """Check if claiming this cell would disconnect enemy territory."""
        # Temporarily remove cell and check connectivity
        neighbors = self.grid.get_neighbors(cell.hex)
        faction_neighbors = [n for n in neighbors if n.owner == faction_color and not n.is_home]
        
        if len(faction_neighbors) < 2:
            return False  # Not a connection point
        
        # Simple heuristic: if cell has multiple same-faction neighbors, it's likely a connection point
        return True
    
    def _find_shortest_reconnection_path(self, disconnected_cell: HexCell, home_cells: List[HexCell], connected: Set[Hex]) -> Optional[List[Hex]]:
        """Find shortest path to reconnect a disconnected cell to home base.
        
        The path must start from a hex adjacent to connected territory and lead to the disconnected cell.
        Only returns valid paths where the first hex is reachable from connected territory.
        
        Args:
            disconnected_cell: The cell to reconnect
            home_cells: List of home base cells
            connected: Set of hexes connected to home base
            
        Returns:
            List of hex positions forming the path, or None if no path exists
        """
        # Simple breadth-first search
        from collections import deque
        
        queue = deque([(disconnected_cell.hex, [])])
        visited = {disconnected_cell.hex}
        
        while queue:
            current, path = queue.popleft()
            
            for neighbor in self.grid.get_neighbors(current):
                if neighbor.hex in visited:
                    continue
                
                visited.add(neighbor.hex)
                new_path = path + [neighbor.hex]
                
                # If we reached connected territory, return the path
                if neighbor.hex in connected:
                    # Reverse the path so it starts from connected territory
                    return list(reversed(new_path))
                
                # If cell is claimable (owned by enemy or unclaimed), continue search
                if neighbor.owner != self.faction.color:
                    queue.append((neighbor.hex, new_path))
        
        return None
    
    def _calculate_mission_cost(self, mission_type: str, target: Hex) -> int:
        """Calculate cost of a mission with sector-based modifiers.
        
        Base cost is modified by:
        1. Distance from center (original behavior)
        2. Sector ownership: If the target is in another faction's native sector,
           cost increases based on proximity to that faction's home base
        
        Cost multipliers for cross-sector operations:
        - BASE_CROSS_SECTOR_MULTIPLIER: 1.5 (50% increase for operating in non-native sector)
        - MAX_PROXIMITY_MULTIPLIER: 3.0 (3x cost when very close to native faction's base)
        - Proximity multiplier decreases linearly with distance from native base
        """
        # Base costs for each mission type
        base_costs = {
            'claim': 1000,
            'disrupt': 5000,
            'reclaim': 3000
        }
        
        # Start with base cost
        distance = target.distance_from_center()
        cost = base_costs[mission_type] * (1 + distance * 0.05)
        
        # Get the target cell to check its native sector
        target_cell = self.grid.get_cell(target)
        
        if target_cell and target_cell.native_sector:
            native_sector = target_cell.native_sector
            
            # If operating in another faction's native sector, apply penalty
            if native_sector != self.faction.color:
                # Get the native faction's home base for distance calculation
                native_home_base = self.grid.get_faction_home_base(native_sector)
                
                if native_home_base:
                    # Calculate distance from target to native faction's home base
                    distance_to_native_base = target.distance_to(native_home_base)
                    
                    # Cross-sector base multiplier
                    BASE_CROSS_SECTOR_MULTIPLIER = 1.5
                    
                    # Maximum proximity multiplier (when right next to native base)
                    MAX_PROXIMITY_MULTIPLIER = 3.0
                    
                    # Distance at which proximity penalty becomes negligible (12 hexes)
                    PROXIMITY_DISTANCE_THRESHOLD = 12
                    
                    # Calculate proximity multiplier (higher when closer to native base)
                    # Linear decay from MAX at distance 0 to 1.0 at THRESHOLD
                    if distance_to_native_base < PROXIMITY_DISTANCE_THRESHOLD:
                        proximity_factor = 1.0 - (distance_to_native_base / PROXIMITY_DISTANCE_THRESHOLD)
                        proximity_multiplier = 1.0 + proximity_factor * (MAX_PROXIMITY_MULTIPLIER - 1.0)
                    else:
                        proximity_multiplier = 1.0
                    
                    # Apply both cross-sector and proximity multipliers
                    cost *= BASE_CROSS_SECTOR_MULTIPLIER * proximity_multiplier
        
        return int(cost)
    
    def execute_mission(self, mission: Mission, current_hour: int) -> bool:
        """Execute a mission if possible.
        
        Enforces strict contiguity: missions can only target hexes adjacent to 
        connected faction territory (with a path from home base).
        """
        # Check if faction can afford it
        if not self.faction.spend_credits(mission.cost):
            return False
        
        # Calculate required mercenaries
        required_mercs = max(1, mission.cost // 10000)
        
        # Check if mercenaries available
        if not self.mercenary_pool.allocate(required_mercs, current_hour):
            self.faction.add_credits(mission.cost)  # Refund
            return False
        
        # Get connected territory for contiguity check
        home_cells = self.grid.get_home_cells(self.faction.color)
        connected = self.grid.find_connected_cells(home_cells)
        
        # Execute mission based on type
        target_cell = self.grid.get_cell(mission.target)
        
        if mission.type == 'claim':
            # Can only claim unclaimed territory (owner is None)
            # Cannot claim permanently owned territories
            # Must be adjacent to connected territory
            if (target_cell and target_cell.owner is None and not target_cell.is_permanent
                    and self._is_hex_reachable(mission.target, connected)):
                target_cell.owner = self.faction.color
                target_cell.set_protection(current_hour, 3)
                
                # Protect adjacent same-faction cells
                for neighbor in self.grid.get_neighbors(mission.target):
                    if neighbor.owner == self.faction.color:
                        neighbor.set_protection(current_hour, 3)
                
                # Expand grid if this was an edge hex
                self._expand_grid_if_needed(mission.target)
                success = True
            else:
                success = False
        
        elif mission.type in ['disrupt', 'reclaim']:
            # Cannot disrupt/reclaim permanently owned territories or home bases
            # Must be adjacent to connected territory
            if (target_cell and target_cell.owner not in [None, self.faction.color] 
                    and not target_cell.is_home and not target_cell.is_permanent
                    and self._is_hex_reachable(mission.target, connected)):
                if not target_cell.is_protected(current_hour):
                    target_cell.owner = self.faction.color
                    target_cell.set_protection(current_hour, 3)
                    
                    # Protect adjacent same-faction cells
                    for neighbor in self.grid.get_neighbors(mission.target):
                        if neighbor.owner == self.faction.color:
                            neighbor.set_protection(current_hour, 3)
                    
                    success = True
                else:
                    success = False
            else:
                success = False
        else:
            success = False
        
        # Note: Mercenaries are now automatically released after 0.5 hours
        # No need to manually release them here
        
        if not success:
            self.faction.add_credits(mission.cost)  # Refund if mission failed
        
        return success
    
    def _expand_grid_if_needed(self, claimed_hex: Hex):
        """Expand grid if an edge hex was claimed."""
        # Check if any neighbor doesn't exist
        for neighbor_hex in claimed_hex.neighbors():
            if neighbor_hex not in self.grid.cells:
                self.grid.expand_grid(neighbor_hex)
