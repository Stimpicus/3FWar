# 3FWar

## Hex-Grid Territory Control Simulation

A strategic simulation where three factions (Orange, Green, and Blue) compete for territorial dominance and wealth accumulation through tactical expansion, disruption, and resource management.

<img width="684" height="737" alt="image" src="https://github.com/user-attachments/assets/baf8009c-7384-4c9a-ad4e-3de366e3e088" />

## Quick Start

### Installation

1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

**Visual Interface:**
```bash
python main.py
```

**Examples & Testing:**
```bash
python examples.py  # Run usage examples
python test_sim.py  # Run simulation tests
```

## Game Mechanics

### Overview

## Game Mechanics

### Overview

I want to build a simulation with the following definitions and parameters from the above image.

All of the grey, orange, green, and blue hexes pictured above are static and should be considered "Owned" by their representative colors (factions.) These blocks of color will define the "Home base" for each color.

The image above should be at the center of a hex-grid with the ability to expand infinitely, as needed, by generating new hexes only when an existing "edge" hex is claimed. However, the hex-grid will only expand one hex at a time, and will never contract to a size smaller than in the shared image.

The orange, green, and blue hexes represent three distinct factions defined by their color.

The goal of each faction is to make as much money as possible.

At the start of every week each faction will 1,000,000,000 credits.

Factions may claim un-claimed (yellow) territory (hexes) adjacent to an owned or claimed territory by offering "Claim" missions to mercenaries

At the end of every hour, all faction claimed hexes with a contiguous line of faction claimed hexes to the faction home base will produce resources. The value of these resources scale based on their distance from the grey hex at the center of the image shared above.

At the end of every day, all faction claimed territories will deposit theior produced resources into the faction home-base

Each faction will have access to a single shared finite pool of mercenaries. The size of this mercenary pool is not fixed, it can expand and contract over time but should never drop below 300 and never exceed 5,000.

Each faction is fully aware of the global map state and individual faction incomes at all times.

Factions may claim territory previously claimed by opposing factions in order to disrupt their "supply line" by breaking the contiguous link of territories claimed by the opposing faction. Ths is completed by offering "Disrupt" missions to mercenaries. 

Factions may re-claim territory separating their home base from another claimed body of territories by offering "Reclaim" missions to mercenaries.

Should a body of faction claimed territories be separated from the faction home territory, the remote territory will no longer be eligible for expansion until/unless a connection to their faction's home territory is re-established.

At the start of every hour, any body of claimed territory with no contiguous link to the owning faction's base territories will shrink by one full length. These territories are "Reclaimed"

When a territory is reclaimed, all previously generated and not-yet deposited resources will be lost and its' status will be reset to Unclaimed.

When a territory is reclaimed, all adjacent territories will be evaluated. Any unclaimed territory with no bordering claimed territory should be removed from the map.

When a territory is claimed, it and all adjacent territories claimed by the same faction will be protected from Disurpt and Relcaim missions for a period of three hours.

Each faction must compete with the others by hiring mercenaries to perform one of the available mission types: Claim, Disrupt, and Reclaim.

Factions must develop strategies to expand their territory to receive more resources, reduce opposing factions' territories through targeted disrupt missions seeking to break contiguous territories, and re-claim their own territories to prevent supply line disruption of their own.

I'd like to request a Github Agent create a Python application to perform this simulation.

The application should display a graphical representation of the hex map.

The application should display the following metrics for each faction in real-time: Net worth, current daily production, 

The application should allow the following actions: Start simulation, Pause simulation, Reset simulation, Save simulation data, Load simulation data, Adjust simulation speed scaling between 0 and 4 with a value of 1 representing 1 simulated hour every real-world second.

## Controls

- **SPACE**: Start/Pause simulation
- **R**: Reset simulation to initial state
- **S**: Save simulation state to `simulation_save.json`
- **L**: Load simulation state from `simulation_save.json`
- **+/-**: Adjust simulation speed (0-4, where 1 = 1 simulated hour per second)
- **Arrow Keys**: Pan camera view
- **Mouse Wheel**: Zoom in/out

## Display Features

The application displays:
- **Hex Map**: Visual representation of all territories
  - Grey: Neutral home base (center)
  - Orange/Green/Blue: Faction home bases and claimed territories
  - Yellow: Unclaimed territories available for expansion
- **Real-time Metrics** (per faction):
  - Net worth (credits + resources)
  - Current credits
  - Daily production
  - Territory count
- **Time Tracking**: Current week, day, and hour
- **Mercenary Pool**: Available mercenaries (shared resource)

## Architecture

The simulation consists of several key modules:

- **`hex_grid.py`**: Hex coordinate system and grid management
  - Axial coordinate system for hexagons
  - Dynamic grid expansion/contraction
  - Neighbor finding and pathfinding utilities

- **`faction.py`**: Faction AI and mission management
  - Three mission types: Claim, Disrupt, Reclaim
  - AI decision-making for strategic expansion
  - Mercenary pool management

- **`simulation.py`**: Core simulation engine
  - Hourly, daily, and weekly event processing
  - Resource production and territory mechanics
  - State serialization for save/load

- **`main.py`**: Pygame-based visual interface
  - Hex rendering with zoom and pan
  - Real-time metrics display
  - User controls and interaction

## Implementation Details

### Resource Production
- Connected territories produce resources every hour
- Resource value scales with distance from center: `base_value * (1 + distance * 0.1)`
- Resources are deposited to faction home base at the end of each day

### Territory Protection
- Newly claimed hexes and adjacent same-faction hexes are protected for 3 hours
- Protected hexes cannot be targeted by Disrupt or Reclaim missions

### Disconnected Territories
- Territories without a contiguous path to the home base stop producing resources
- Disconnected territories shrink by 1 hex per hour (edge cells first)
- When a territory is reclaimed, accumulated resources are forfeited

### Grid Dynamics
- Grid expands when edge hexes are claimed (adds new neighbors)
- Unclaimed hexes with no claimed neighbors are removed from the map
- Grid never contracts below its initial size

### Mission Costs
- **Claim**: Base cost 1,000 credits × (1 + distance × 0.05)
- **Disrupt**: Base cost 5,000 credits × (1 + distance × 0.05)
- **Reclaim**: Base cost 3,000 credits × (1 + distance × 0.05)

## Files

- `main.py` - Main application with pygame interface
- `simulation.py` - Core simulation engine
- `hex_grid.py` - Hex grid and coordinate system
- `faction.py` - Faction AI and missions
- `test_sim.py` - Simulation tests
- `examples.py` - Usage examples
- `create_screenshot.py` - Screenshot generation utility
- `requirements.txt` - Python dependencies
- `RUNNING.md` - Detailed running instructions

## Development

### Testing
```bash
python test_sim.py
```

### Examples
```bash
python examples.py
```

### Creating Screenshots
```bash
python create_screenshot.py
```

## License

This project is open source and available for educational and personal use.
