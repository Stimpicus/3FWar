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
        self.credits = 1_000_000_000  # Start with 1 billion credits
        self.total_resources = 0.0
        self.daily_production = 0.0
        self.net_worth = self.credits
    
    def add_credits(self, amount: float):
        """Add credits to faction."""
        self.credits += amount
        self.net_worth = self.credits + self.total_resources
    
    def spend_credits(self, amount: float) -> bool:
        """Spend credits if available."""
        if self.credits >= amount:
            self.credits -= amount
            self.net_worth = self.credits + self.total_resources
            return True
        return False
    
    def add_resources(self, amount: float):
        """Add resources to faction."""
        self.total_resources += amount
        self.net_worth = self.credits + self.total_resources
    
    def weekly_reset(self):
        """Reset weekly credits."""
        self.credits = 1_000_000_000
        self.net_worth = self.credits + self.total_resources


class MercenaryPool:
    """Manages the shared mercenary pool."""
    
    def __init__(self, initial_size: int = 1000):
        self.size = initial_size
        self.min_size = 300
        self.max_size = 5000
    
    def allocate(self, count: int) -> bool:
        """Allocate mercenaries for a mission."""
        if self.size >= count:
            self.size -= count
            return True
        return False
    
    def release(self, count: int):
        """Release mercenaries back to pool."""
        self.size = min(self.size + count, self.max_size)
    
    def adjust_size(self, delta: int):
        """Adjust pool size within bounds."""
        self.size = max(self.min_size, min(self.max_size, self.size + delta))


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
                path = self._find_shortest_reconnection_path(cell, home_cells)
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
        """Find enemy cells that would break supply lines if claimed."""
        targets = []
        other_factions = ['orange', 'green', 'blue']
        other_factions.remove(self.faction.color)
        
        for enemy_color in other_factions:
            enemy_cells = self.grid.get_faction_cells(enemy_color)
            enemy_home = self.grid.get_home_cells(enemy_color)
            
            if not enemy_home:
                continue
            
            # Find cells that are critical connection points
            for cell in enemy_cells:
                if cell.is_home or cell.is_protected(current_hour):
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
    
    def _find_shortest_reconnection_path(self, disconnected_cell: HexCell, home_cells: List[HexCell]) -> Optional[List[Hex]]:
        """Find shortest path to reconnect a disconnected cell to home base."""
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
                
                # If we reached a home cell, return path
                if neighbor in home_cells or (neighbor.owner == self.faction.color and 
                                               neighbor.hex in self.grid.find_connected_cells(home_cells)):
                    return new_path
                
                # If cell is claimable (owned by enemy or unclaimed), continue search
                if neighbor.owner != self.faction.color:
                    queue.append((neighbor.hex, new_path))
        
        return None
    
    def _calculate_mission_cost(self, mission_type: str, target: Hex) -> int:
        """Calculate cost of a mission."""
        base_costs = {
            'claim': 1000,
            'disrupt': 5000,
            'reclaim': 3000
        }
        
        distance = target.distance_from_center()
        cost = base_costs[mission_type] * (1 + distance * 0.05)
        
        return int(cost)
    
    def execute_mission(self, mission: Mission, current_hour: int) -> bool:
        """Execute a mission if possible."""
        # Check if faction can afford it
        if not self.faction.spend_credits(mission.cost):
            return False
        
        # Calculate required mercenaries
        required_mercs = max(1, mission.cost // 10000)
        
        # Check if mercenaries available
        if not self.mercenary_pool.allocate(required_mercs):
            self.faction.add_credits(mission.cost)  # Refund
            return False
        
        # Execute mission based on type
        target_cell = self.grid.get_cell(mission.target)
        
        if mission.type == 'claim':
            # Can only claim unclaimed territory (owner is None)
            # Cannot claim permanently owned territories
            if target_cell and target_cell.owner is None and not target_cell.is_permanent:
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
            if target_cell and target_cell.owner not in [None, self.faction.color] and not target_cell.is_home and not target_cell.is_permanent:
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
        
        # Release mercenaries
        self.mercenary_pool.release(required_mercs)
        
        if not success:
            self.faction.add_credits(mission.cost)  # Refund if mission failed
        
        return success
    
    def _expand_grid_if_needed(self, claimed_hex: Hex):
        """Expand grid if an edge hex was claimed."""
        # Check if any neighbor doesn't exist
        for neighbor_hex in claimed_hex.neighbors():
            if neighbor_hex not in self.grid.cells:
                self.grid.expand_grid(neighbor_hex)
