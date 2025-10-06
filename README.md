# 3FWar

<img width="684" height="737" alt="image" src="https://github.com/user-attachments/assets/baf8009c-7384-4c9a-ad4e-3de366e3e088" />

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
