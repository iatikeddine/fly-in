*This project has been created as part of the 42 curriculum by iatikedd.*

# Fly-in

## Description
**Fly-in** is an algorithmic routing system designed to efficiently navigate a fleet of autonomous drones through a network of connected zones. The primary goal of the project is to minimize the total number of simulation turns required to move all drones from a central base (`start_hub`) to a target location (`end_hub`) while strictly adhering to movement rules, zone capacities, and path constraints. 

## Algorithm Choices and Implementation Strategy
The core engine of this project relies on a strictly typed, object-oriented approach divided into three main components:

1. **Graph Parsing & Representation**: 
   A custom parser reads the map format and generates a network of `Zone` and `Connection` objects. Constraints such as `max_drones` and `max_link_capacity` are mapped directly to instance properties.

2. **Weighted Dijkstra Pathfinding**: 
   The `Algorithm` class utilizes a weighted Dijkstra search (via `heapq`) to find optimal routes. Edge weights are dynamically assigned based on the destination zone type: `priority` zones are cheaper (weight: 99), `normal` zones are standard (weight: 100), `restricted` zones are penalized (weight: 200), and `blocked` zones are completely ignored.
   To prevent massive traffic jams on a single route, the algorithm iteratively penalizes the edges of the first discovered path to mathematically find a distinct, highly-efficient "second path".

3. **Simulation Engine (The Zipper Loop)**: 
   To maximize throughput across two parallel paths, the `Simulation` class evaluates drone movements *backward* (from the finish line down to the start). This entirely eliminates "self-blocking" traffic jams. Furthermore, the simulation alternates which path receives priority on every single turn—acting as a perfect "zipper merge" for drones sharing bottleneck connections. 

## Visual Representation Features
The project features a highly customizable **Colored Terminal Output** engine. 
- Map files can define arbitrary colors via the `[color=...]` metadata tag on any zone.
- The `ColoredPrint` class automatically maps these string values to precise 256-color ANSI escape sequences.
- It includes a special `rainbow` mode that cycles colors per-character.
- **Enhancement**: This visual representation makes it instantly clear where drones are bottlenecking during complex simulations, turning an otherwise massive wall of text into an easily readable, color-coded traffic map.

## Example Input and Expected Output

**Example Map (`test_map.txt`):**
```text
nb_drones: 2
start_hub: start 0 0 [color=green]
end_hub: goal 10 10 [color=gold]
hub: roof1 3 4 [zone=normal color=blue]

connection: start-roof1
connection: roof1-goal
```

**Terminal Output:**
```text
D1-roof1 D2-roof1
D1-goal D2-goal

2
```
*(Note: In the actual terminal, the drone movements are colored blue and gold respectively).*

## Instructions
This project requires **Python 3.10+**. A `Makefile` is provided for automation:

- **`make install`**: Install any required project dependencies.
- **`make run (ARG)`**: Execute the main simulation on the provided test map (ARG).
- **`make debug (ARG)`**: Run the simulation in debug mode.
- **`make clean`**: Remove temporary files and python caches (.mypy_cache, `__pycache__`).
- **`make clean`**: Remove temporary files and python caches (`.mypy_cache`, `__pycache__`).
- **`make lint`**: Run strict static analysis using `flake8` and `mypy`.

## Resources
- [Graph theory (Youtube)] (https://www.youtube.com/watch?v=LFKZLXVO-Dg)
- [Dijkstra's Algorithm (Youtube)] (https://www.youtube.com/watch?v=GazC3A4OQTE&t=54s)

**AI Usage Statement:**
AI was utilized  to assist with the formatting and writing of this README file, and to validate static type hints for `mypy` compliance across the codebase.
