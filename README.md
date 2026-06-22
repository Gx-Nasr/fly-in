*This project has been created as part of the 42 curriculum by nel-adao.*

# Description

## Project Overview

Fly-in is a drone routing and traffic control simulation project.

The goal of the project is to find valid paths for multiple drones travelling from a start hub to an end hub while respecting several traffic constraints such as:

* Hub capacity (`max_drones`)
* Connection capacity (`max_link_capacity`)
* Restricted zones
* Blocked zones
* Priority zones

The program parses a map description file, validates its syntax and logic, computes paths for all drones using a reservation-based pathfinding algorithm, and displays both a textual and graphical representation of the simulation.

## Main Features

* Custom map parser with detailed error handling.
* Validation of map syntax and logical constraints.
* Multi-drone pathfinding.
* Reservation system to avoid collisions.
* Support for special zone types:

  * normal
  * restricted
  * blocked
  * priority
* Interactive visualization using Matplotlib.
* Turn-by-turn drone movement simulation.

# Instructions

## Installation

Create a virtual environment and install dependencies:

```bash
uv sync
```

or

```bash
make install
```

## Run

```bash
make run MAP=maps/example.txt
```

## Debug

```bash
make debug MAP=maps/example.txt
```

## Lint

```bash
make lint
```

Optional strict mode:

```bash
make lint-strict
```

## Clean Cache Files

```bash
make clean
```

# Algorithm Choices and Implementation Strategy

## Pathfinding

The project uses a modified Dijkstra algorithm.

Unlike a traditional shortest-path search, each state contains:

```text
(zone, turn)
```

instead of only:

```text
(zone)
```

This allows the algorithm to reason about time and drone reservations.

### Reservation System

After a drone path is found:

* Every occupied zone is reserved.
* Every traversed connection is reserved.
* Future drones must respect these reservations.

This prevents collisions and ensures that hub and connection capacities are never exceeded.

### Zone Types

#### Normal

Standard movement cost:

```text
cost = 1
```

#### Restricted

Entering the zone requires:

```text
cost = 2
```

which simulates slower traversal.

#### Blocked

The zone cannot be traversed.

#### Priority

Priority zones receive a better exploration priority during pathfinding.

# Visual Representation

The project includes a graphical visualization built with Matplotlib.

## Features

* Background map image.
* Display of all hubs and connections.
* Color-coded zones.
* Interactive drone visualization.
* Turn-by-turn navigation using keyboard controls.
* Full-screen display mode.

## User Experience Benefits

The visual interface makes it easier to:

* Understand drone movements.
* Observe congestion points.
* Verify pathfinding results.
* Debug routing behavior.
* Analyze traffic flow over time.

Compared to textual output alone, the visualization provides a more intuitive understanding of how drones interact with the environment.

# Resources

## Documentation

* Python Documentation
  https://docs.python.org/3/

* Dataclasses Documentation
  https://docs.python.org/3/library/dataclasses.html

* Heap Queue (heapq) Documentation
  https://docs.python.org/3/library/heapq.html

* Matplotlib Documentation
  https://matplotlib.org/stable/

## Tutorials

* Dijkstra Algorithm Tutorial
  https://youtu.be/EFg3u_E6eHU

* Graph Theory and Pathfinding Tutorial
  https://youtu.be/XB4MIexjvY0

## Peer Learning

Several implementation ideas and project discussions were improved through peer learning sessions with other 42 students, particularly regarding:

* Parser validation strategies
* Pathfinding logic
* Reservation management
* Visualization design

## AI Usage

AI tools were used as learning assistants during the project.

Their usage was limited to:

* Understanding project requirements.
* Exploring different implementation approaches.
* Generating parser test cases.
* Reviewing documentation and explanations of Python concepts.
* Identifying potential edge cases during development.

All project architecture, implementation, debugging, and final design decisions were performed manually by the project author.
