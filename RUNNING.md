# Running the 3FWar Simulation

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

## Controls

- **SPACE**: Start/Pause simulation
- **R**: Reset simulation to initial state
- **S**: Save simulation state to file
- **L**: Load simulation state from file
- **+/-**: Adjust simulation speed (0-4, where 1 = 1 simulated hour per second)
- **Arrow Keys**: Pan camera view
- **Mouse Wheel**: Zoom in/out

## Game Mechanics

### Factions
- Three factions compete: Orange, Green, and Blue
- Each faction starts with 1,000,000,000 credits per week
- Goal: Maximize net worth through territorial expansion

### Territory Control
- **Claim**: Expand into adjacent unclaimed (yellow) hexes
- **Disrupt**: Take enemy territory to break their supply lines
- **Reclaim**: Recover lost territory to reconnect disconnected areas

### Resource Production
- Connected territories produce resources every hour
- Resource value scales with distance from center (farther = more valuable)
- Resources are deposited to faction home base daily

### Territory Mechanics
- Newly claimed hexes are protected for 3 hours
- Disconnected territories shrink by 1 hex per hour until reconnected
- Grid expands dynamically when edge hexes are claimed
- Orphaned unclaimed hexes are removed from the map

### Mercenaries
- Shared pool of mercenaries (300-5,000)
- Factions compete to hire mercenaries for missions
- Mission costs vary by type and distance

## Display

The application shows:
- **Hex Map**: Visual representation of all territories
  - Grey: Neutral home base
  - Orange/Green/Blue: Faction territories
  - Yellow: Unclaimed territories
- **Faction Metrics**: Real-time display of:
  - Net worth
  - Current credits
  - Daily production
  - Territory count
- **Time**: Current week, day, and hour
- **Mercenary Pool**: Available mercenaries
