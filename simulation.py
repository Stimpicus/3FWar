"""Main simulation engine."""
from typing import List, Set
from hex_grid import Hex, HexGrid, HexCell
from faction import Faction, FactionAI, MercenaryPool


class Simulation:
    """Main simulation engine."""
    
    def __init__(self):
        self.grid = HexGrid()
        self.mercenary_pool = MercenaryPool(initial_size=300)
        
        # Create factions
        self.factions = {
            'orange': Faction('Orange', 'orange'),
            'green': Faction('Green', 'green'),
            'blue': Faction('Blue', 'blue')
        }
        
        # Create faction AIs
        self.faction_ais = {
            color: FactionAI(faction, self.grid, self.mercenary_pool)
            for color, faction in self.factions.items()
        }
        
        # Simulation state
        self.current_hour = 0
        self.current_day = 0
        self.current_week = 0
        self.running = False
    
    def reset(self):
        """Reset simulation to initial state."""
        self.grid = HexGrid()
        self.mercenary_pool = MercenaryPool(initial_size=300)
        
        # Reset factions
        for faction in self.factions.values():
            faction.credits = 10_000
            faction.daily_production = 0.0
        
        # Reset AIs
        for color, faction in self.factions.items():
            self.faction_ais[color] = FactionAI(faction, self.grid, self.mercenary_pool)
        
        self.current_hour = 0
        self.current_day = 0
        self.current_week = 0
    
    def step_hour(self):
        """Execute one hour of simulation."""
        self.current_hour += 1
        
        # Every 24 hours is a new day
        if self.current_hour % 24 == 0:
            self.current_day += 1
        
        # Every 168 hours (7 days) is a new week
        if self.current_hour % 168 == 0:
            self.current_week += 1
            self._process_weekly()
        
        # Process hourly events at the start of each hour
        self._process_hourly()
        
        # Process daily events at the end of each day
        if self.current_hour % 24 == 0:
            self._process_daily()
        
        # Factions make decisions and execute missions
        self._process_faction_actions()
    
    def _process_hourly(self):
        """Process hourly events."""
        # 1. Process mercenary missions (release completed missions)
        self.mercenary_pool.process_hour(self.current_hour)
        
        # 2. Shrink disconnected territories
        self._shrink_disconnected_territories()
        
        # 3. Produce resources for connected territories
        self._produce_resources()
    
    def _process_daily(self):
        """Process daily events."""
        # Deposit resources to faction accounts as credits
        for color, faction in self.factions.items():
            home_cells = self.grid.get_home_cells(color)
            faction_cells = self.grid.get_faction_cells(color)
            
            if not home_cells:
                continue
            
            # Calculate connected territory
            connected = self.grid.find_connected_cells(home_cells)
            
            # Collect resources from connected cells and add directly to credits
            total_deposited = 0.0
            for cell in faction_cells:
                if cell.hex in connected:
                    total_deposited += cell.deposit_resources()
            
            faction.add_credits(total_deposited)
            
            # Update daily production metric
            faction.daily_production = total_deposited
    
    def _process_weekly(self):
        """Process weekly events."""
        # Reset faction credits
        for faction in self.factions.values():
            faction.weekly_reset()
    
    def _shrink_disconnected_territories(self):
        """Shrink disconnected territories by one hex per hour."""
        for color, faction in self.factions.items():
            home_cells = self.grid.get_home_cells(color)
            faction_cells = self.grid.get_faction_cells(color)
            
            if not home_cells:
                continue
            
            # Find connected territory
            connected = self.grid.find_connected_cells(home_cells)
            
            # Find disconnected cells
            disconnected = [cell for cell in faction_cells if cell.hex not in connected and not cell.is_home]
            
            if not disconnected:
                continue
            
            # Group disconnected cells into separate bodies
            bodies = self._find_territory_bodies(disconnected)
            
            # Shrink each body by removing edge cells
            for body in bodies:
                edge_cells = self._find_edge_cells(body)
                
                # Remove one edge cell per body per hour
                if edge_cells:
                    cell_to_remove = edge_cells[0]
                    cell_to_remove.reset()
                    
                    # Check for orphaned unclaimed neighbors
                    self._remove_orphaned_hexes(cell_to_remove.hex)
    
    def _find_territory_bodies(self, cells: List[HexCell]) -> List[Set[HexCell]]:
        """Group cells into separate connected bodies."""
        if not cells:
            return []
        
        unvisited = set(cells)
        bodies = []
        
        while unvisited:
            # Start new body
            start = unvisited.pop()
            body = {start}
            frontier = [start]
            
            while frontier:
                current = frontier.pop()
                for neighbor in self.grid.get_neighbors(current.hex):
                    if neighbor in unvisited:
                        unvisited.remove(neighbor)
                        body.add(neighbor)
                        frontier.append(neighbor)
            
            bodies.append(body)
        
        return bodies
    
    def _find_edge_cells(self, body: Set[HexCell]) -> List[HexCell]:
        """Find edge cells of a territory body (cells with fewer same-owner neighbors)."""
        edge_cells = []
        
        for cell in body:
            neighbors = self.grid.get_neighbors(cell.hex)
            same_owner_neighbors = [n for n in neighbors if n in body]
            
            # Edge cells have fewer same-owner neighbors
            if len(same_owner_neighbors) < 6:
                edge_cells.append(cell)
        
        # Sort by fewest neighbors first (most isolated)
        edge_cells.sort(key=lambda c: len([n for n in self.grid.get_neighbors(c.hex) if n in body]))
        
        return edge_cells
    
    def _remove_orphaned_hexes(self, reclaimed_hex: Hex):
        """Remove adjacent unclaimed hexes that have no claimed neighbors."""
        for neighbor_hex in reclaimed_hex.neighbors():
            neighbor = self.grid.get_cell(neighbor_hex)
            
            if not neighbor or neighbor.owner is not None:
                continue
            
            # Check if this unclaimed hex has any claimed neighbors
            has_claimed_neighbor = False
            for n in self.grid.get_neighbors(neighbor_hex):
                if n.owner is not None:
                    has_claimed_neighbor = True
                    break
            
            if not has_claimed_neighbor:
                self.grid.remove_hex(neighbor_hex)
    
    def _produce_resources(self):
        """Produce resources for all connected faction territories."""
        for color, faction in self.factions.items():
            home_cells = self.grid.get_home_cells(color)
            faction_cells = self.grid.get_faction_cells(color)
            
            if not home_cells:
                continue
            
            # Find connected territory
            connected = self.grid.find_connected_cells(home_cells)
            
            # Produce resources for connected cells
            for cell in faction_cells:
                if cell.hex in connected:
                    cell.produce_resources()
    
    def _process_faction_actions(self):
        """Process faction AI decisions and mission execution."""
        import random
        
        # Randomize faction order each hour for fairness
        faction_colors = list(self.factions.keys())
        random.shuffle(faction_colors)
        
        for color in faction_colors:
            faction = self.factions[color]
            ai = self.faction_ais[color]
            
            # Get proposed missions
            missions = ai.evaluate_missions(self.current_hour)
            
            # Execute missions in order of priority
            for mission in missions:
                # Random chance to execute (simulate decision making)
                if random.random() < 0.3:  # 30% chance to execute each mission
                    ai.execute_mission(mission, self.current_hour)
    
    def get_state(self) -> dict:
        """Get current simulation state for display."""
        return {
            'hour': self.current_hour,
            'day': self.current_day,
            'week': self.current_week,
            'factions': {
                color: {
                    'credits': faction.credits,
                    'daily_production': faction.daily_production,
                    'territory_count': len(self.grid.get_faction_cells(color))
                }
                for color, faction in self.factions.items()
            },
            'mercenary_pool': self.mercenary_pool.size,
            'mercenary_available': self.mercenary_pool.get_available_count(self.current_hour)
        }
    
    def save_state(self) -> dict:
        """Serialize simulation state for saving."""
        cells_data = {}
        for hex_pos, cell in self.grid.cells.items():
            cells_data[f"{hex_pos.q},{hex_pos.r}"] = {
                'owner': cell.owner,
                'is_home': cell.is_home,
                'is_permanent': cell.is_permanent,
                'resources': cell.resources,
                'protection_until': cell.protection_until
            }
        
        # Save mercenary states
        mercenaries_data = []
        for merc in self.mercenary_pool.mercenaries:
            mercenaries_data.append({
                'id': merc.id,
                'assigned': merc.assigned,
                'mission_complete_hour': merc.mission_complete_hour
            })
        
        return {
            'current_hour': self.current_hour,
            'current_day': self.current_day,
            'current_week': self.current_week,
            'mercenary_pool_size': self.mercenary_pool.size,
            'mercenaries': mercenaries_data,
            'factions': {
                color: {
                    'credits': faction.credits,
                    'daily_production': faction.daily_production
                }
                for color, faction in self.factions.items()
            },
            'cells': cells_data
        }
    
    def load_state(self, state: dict):
        """Deserialize and load simulation state."""
        self.current_hour = state['current_hour']
        self.current_day = state['current_day']
        self.current_week = state['current_week']
        
        # Load mercenary pool
        if 'mercenaries' in state:
            # New format with individual mercenaries
            from faction import Mercenary
            self.mercenary_pool.mercenaries = []
            for merc_data in state['mercenaries']:
                merc = Mercenary(merc_data['id'])
                merc.assigned = merc_data['assigned']
                merc.mission_complete_hour = merc_data['mission_complete_hour']
                self.mercenary_pool.mercenaries.append(merc)
        else:
            # Old format - just set size (backwards compatibility)
            self.mercenary_pool.size = state.get('mercenary_pool_size', 300)
        
        # Load faction data
        for color, faction_data in state['factions'].items():
            faction = self.factions[color]
            faction.credits = faction_data['credits']
            faction.daily_production = faction_data.get('daily_production', 0.0)
            # Ignore old total_resources and net_worth fields for backwards compatibility
        
        # Load grid cells
        from hex_grid import Hex, HexCell
        self.grid.cells.clear()
        
        for hex_str, cell_data in state['cells'].items():
            q, r = map(int, hex_str.split(','))
            hex_pos = Hex(q, r)
            is_permanent = cell_data.get('is_permanent', False)  # Default to False for backwards compatibility
            cell = HexCell(hex_pos, cell_data['owner'], cell_data['is_home'], is_permanent)
            cell.resources = cell_data['resources']
            cell.protection_until = cell_data['protection_until']
            self.grid.cells[hex_pos] = cell
