# Fly-In

![Python](https://img.shields.io/badge/Python-3.14%2B-blue)
![uv](https://img.shields.io/badge/Tooling-uv-111111)
![matplotlib](https://img.shields.io/badge/Visualization-matplotlib-11557c)
![mypy](https://img.shields.io/badge/Type%20Checking-mypy-2b5b84)
![flake8](https://img.shields.io/badge/Lint-flake8-3776ab)

Fly-In is a drone-routing simulator that parses custom map files, builds a zone graph, computes turn-aware paths for multiple drones, and visualizes the resulting traffic flow.

## Overview

The project reads a map definition containing drones, hubs, and connections, then routes each drone from the start hub to the end hub while respecting zone capacity, connection capacity, and zone-specific movement costs. After routing, it prints the per-turn drone movements and opens an interactive matplotlib visualization for stepping through the simulation.

The bundled maps range from simple linear paths to high-pressure scenarios with bottlenecks, loops, restricted zones, priority zones, and tight capacity limits.

## Features

- Custom map parser with detailed validation and error reporting.
- Support for `start_hub`, `hub`, `end_hub`, and bidirectional `connection` declarations.
- Zone metadata for `color`, `zone`, and `max_drones`.
- Connection metadata for `max_link_capacity`.
- Reservation-aware pathfinding that accounts for drone congestion over time.
- Movement cost differences for `normal` and `restricted` zones.
- Priority-zone preference during path selection.
- Turn-by-turn command output for all drones.
- Interactive matplotlib visualization with keyboard navigation.
- Prebuilt map packs for easy, medium, hard, and challenger scenarios.

## Tech Stack

- Python 3.14+
- `uv` for environment synchronization and execution
- `matplotlib` for visualization
- `mypy` for type checking
- `flake8` for linting

## Architecture

Fly-In follows a simple pipeline:

1. `Parser` loads and validates a map file into an in-memory data dictionary.
2. `GraphInit` converts parsed data into typed domain objects (`Zone`, `Connection`, `Drone`, `GraphData`).
3. `PathFinding` computes a path for each drone using a reservation-aware Dijkstra-style search.
4. Each successful path is reserved so later drones avoid occupied zones and saturated links.
5. The simulator prints turn-by-turn movement commands and launches the visualizer.

This design keeps parsing, graph construction, routing, and presentation separated while sharing a common graph model.

## Project Structure

```text
fly-in/
├── Makefile
├── pyproject.toml
├── images/
│   └── background.png
├── maps/
│   ├── README.md
│   ├── easy/
│   ├── medium/
│   ├── hard/
│   └── challenger/
└── src/
    ├── __main__.py
    ├── Errors.py
    ├── data_classes.py
    ├── dijkstra.py
    ├── graph_init.py
    ├── parser.py
    └── visualization.py
```

## Installation

```bash
uv sync
```

The project expects Python 3.14 or newer.

## Usage

Run the simulator against one of the bundled maps:

```bash
uv run python -m src maps/easy/01_linear_path.txt
```

Or use the Makefile target:

```bash
make run Map=maps/easy/01_linear_path.txt
```

Keyboard controls in the visualizer:

- `Right Arrow` advances one turn.
- `Left Arrow` goes back one turn.

## Environment Variables

None.

## API / Modules

- `src/__main__.py`: CLI entry point that wires parsing, graph creation, routing, and visualization.
- `src/parser.py`: Reads the map file and validates drone counts, zone declarations, and connections.
- `src/graph_init.py`: Converts parsed dictionaries into typed domain objects.
- `src/data_classes.py`: Defines the core data model and graph helpers.
- `src/dijkstra.py`: Implements reservation-aware routing and turn-by-turn output.
- `src/visualization.py`: Draws the map and drone positions with matplotlib.
- `src/Errors.py`: Custom exceptions used during parsing and routing.

## Key Functionality

The main business logic lives in the routing layer. Each drone is routed sequentially so its path can be reserved before the next drone is processed. The search accounts for:

- zone occupancy limits via `max_drones`,
- connection throughput via `max_link_capacity`,
- longer traversal through `restricted` zones,
- preference for `priority` zones when paths are otherwise comparable,
- blocked zones that must be avoided entirely.

After all drones are routed, the simulator emits turn-based movement commands and stores the total turn count for the visualizer.

## Future Improvements

- Improve pathfinding heuristics for denser maps.
- Add automated tests for parser edge cases and routing regressions.
- Expand the visualization with richer legends and route overlays.
- Provide a dedicated command-line help message and example map index.

## License

No license file is present in the repository.
