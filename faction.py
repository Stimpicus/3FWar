"""Faction AI and mission management."""
import random
from typing import List, Optional, Set, Dict
from hex_grid import Hex, HexCell, HexGrid


class Mission:
    """Represents a mission offered by a faction."""
    
    def __init__(self, mission_type: str, target_hex: Hex, faction: str, reward: int):
        self.type = mission_type  # 'claim', 'disrupt', 'reclaim'
        self.target = target_hex
        self.faction = faction
        self.reward = reward  # Reward offered to mercenaries, not cost to faction
        

class Faction:
    """Represents a faction in the simulation."""
    
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color
        self.credits = 0  # Factions no longer receive initial credits
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
        """Weekly reset - no longer resets credits."""
        pass  # Factions no longer receive weekly credits


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
                    reward = self._calculate_mission_reward('reclaim', target)
                    missions.append(Mission('reclaim', target, self.faction.color, reward))
        
        # 2. Claim adjacent unclaimed hexes
        claim_targets = self._find_claim_targets(faction_cells, connected, current_hour)
        for target in claim_targets[:5]:  # Limit to 5 claim missions
            reward = self._calculate_mission_reward('claim', target.hex)
            missions.append(Mission('claim', target.hex, self.faction.color, reward))
        
        # 3. Disrupt enemy supply lines
        disrupt_targets = self._find_disrupt_targets(current_hour)
        for target in disrupt_targets[:2]:  # Limit to 2 disrupt missions
            reward = self._calculate_mission_reward('disrupt', target.hex)
            missions.append(Mission('disrupt', target.hex, self.faction.color, reward))
        
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
    
    def _calculate_mission_reward(self, mission_type: str, target: Hex) -> int:
        """Calculate reward for a mission based on territory balance.
        
        Dynamic reward calculation:
        - Claim mission rewards for the faction with the least territories increase proportionally 
          to the number of territories claimed by the faction with the most territories.
        - Disrupt mission rewards targeting the faction with the least territories decrease 
          proportionally to the number of territories claimed by the faction with the most territories.
        - Disrupt mission rewards targeting the faction with the most territories increase 
          proportionally to the number of territories claimed by the faction with the least territories.
        - Claim mission rewards for the faction with the most territories decrease proportionally 
          to the number of territories claimed by the faction with the least territories.
        """
        # Base rewards for each mission type
        base_rewards = {
            'claim': 1000,
            'disrupt': 5000,
            'reclaim': 3000
        }
        
        # Get territory counts
        territory_counts = self._get_territory_counts()
        faction_with_most, most_territories = self._get_faction_with_most_territories(territory_counts)
        faction_with_least, least_territories = self._get_faction_with_least_territories(territory_counts)
        
        # Start with base reward
        reward = base_rewards[mission_type]
        
        # Determine which faction is being affected by this mission
        target_cell = self.grid.get_cell(target)
        
        if mission_type == 'claim':
            # Claim missions benefit the faction executing them
            if self.faction.color == faction_with_least:
                # Faction with least territories gets proportionally higher rewards
                # Scale by ratio of most to least territories (capped at reasonable values)
                if least_territories > 0:
                    multiplier = 1 + (most_territories / max(least_territories, 1) - 1) * 0.5
                    reward = int(reward * min(multiplier, 3.0))  # Cap at 3x
                else:
                    reward = int(reward * 3.0)  # If no territories, max reward
            elif self.faction.color == faction_with_most:
                # Faction with most territories gets proportionally lower rewards
                if most_territories > 0:
                    multiplier = max(0.3, least_territories / max(most_territories, 1))
                    reward = int(reward * multiplier)
        
        elif mission_type == 'disrupt':
            # Disrupt missions target enemy territory
            # Determine who owns the target
            target_owner = target_cell.owner if target_cell else None
            
            if target_owner == faction_with_least:
                # Disrupting faction with least territories gets lower rewards
                if most_territories > 0:
                    multiplier = max(0.3, least_territories / max(most_territories, 1))
                    reward = int(reward * multiplier)
            elif target_owner == faction_with_most:
                # Disrupting faction with most territories gets higher rewards
                if least_territories > 0:
                    multiplier = 1 + (most_territories / max(least_territories, 1) - 1) * 0.5
                    reward = int(reward * min(multiplier, 3.0))  # Cap at 3x
        
        elif mission_type == 'reclaim':
            # Reclaim uses similar logic to claim (benefits the faction executing)
            if self.faction.color == faction_with_least:
                if least_territories > 0:
                    multiplier = 1 + (most_territories / max(least_territories, 1) - 1) * 0.5
                    reward = int(reward * min(multiplier, 3.0))
                else:
                    reward = int(reward * 3.0)
            elif self.faction.color == faction_with_most:
                if most_territories > 0:
                    multiplier = max(0.3, least_territories / max(most_territories, 1))
                    reward = int(reward * multiplier)
        
        return max(100, reward)  # Minimum reward of 100
    
    def execute_mission(self, mission: Mission, current_hour: int) -> bool:
        """Execute a mission if possible.
        
        Enforces strict contiguity: missions can only target hexes adjacent to 
        connected faction territory (with a path from home base).
        
        Missions no longer cost factions credits. Instead, mercenaries receive rewards
        that are not deducted from faction credits.
        """
        # Check if mercenaries available (no longer check if faction can afford it)
        # All mercenaries have equal chance regardless of mission reward
        required_mercs = 1  # Each mission requires 1 mercenary
        
        if not self.mercenary_pool.allocate(required_mercs, current_hour):
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
        # Mission rewards are not deducted from faction credits
        
        return success
    
    def _expand_grid_if_needed(self, claimed_hex: Hex):
        """Expand grid if an edge hex was claimed."""
        # Check if any neighbor doesn't exist
        for neighbor_hex in claimed_hex.neighbors():
            if neighbor_hex not in self.grid.cells:
                self.grid.expand_grid(neighbor_hex)
