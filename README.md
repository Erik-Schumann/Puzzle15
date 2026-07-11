# Puzzle15

A 15-puzzle (sliding tile puzzle) solver. It runs one or more informed-search
configurations (Dijkstra / Greedy / A* / weighted A*, with a choice of
heuristic) against a puzzle board loaded from CSV, then prints and charts how
each configuration compares on move count, time, and nodes explored.

```
$ python app.py
Greedy (Hamming): solved in 46 moves | time 12.30 ms | observed 812 | inserted 1290
Greedy (Manhattan): solved in 38 moves | time 9.10 ms | observed 640 | inserted 990
A* (Hamming): solved in 30 moves | time 145.20 ms | observed 9100 | inserted 14200
A* (Manhattan): solved in 30 moves | time 41.80 ms | observed 2210 | inserted 3450

Comparison chart written to output/comparison.png
```

(Exact numbers vary by board and machine — this just illustrates the shape of
the output.)

## Requirements

- Python 3.9+
- [matplotlib](https://matplotlib.org/) (the only external dependency, used to
  render `output/comparison.png`)

## Installation

```
pip install -r requirements.txt
```

## Quick start

Run the solver with the bundled default configuration and puzzle board:

```
python app.py
```

This reads settings from [`input/config.ini`](input/config.ini),
solves the configured puzzle with each configured search setup, prints a
summary line per configuration, and writes a comparison chart to
`output/comparison.png`.

## Configuring a run

Everything about a run — which puzzle to solve, which search configurations
to try, and how much logging to print — is controlled by `input/config.ini`. See
[docs/CONFIGURATION.md](docs/CONFIGURATION.md) for the full reference,
including:

- how to point `[problem] state` at one of the boards in [`input/`](input/)
  (or your own CSV)
- how to add/edit `[searchagents]` lines to choose heuristics and
  `a`/`b` evaluation weights, plus an optional per-line `track_visited` field
  to allow/disallow that agent from revisiting already-popped states
- how to control `[generalsettings] level` / `log_interval`, and how to cap a
  run with `max_nodes_observed` / `max_fringe_size` (raising `NoSolutionError`
  with a custom message if exceeded)

## Project structure

| Path | Purpose |
|---|---|
| `app.py` | Entry point: reads `input/config.ini`, runs the search(es), prints results, writes `output/comparison.png` |
| `input/config.ini` | Run configuration (puzzle, general settings, search setups) |
| `input/` | Sample puzzle boards as CSV, plus `config.ini` |
| `output/` | Generated `comparison.png` (created automatically if missing) |
| `Problem.py`, `Node.py`, `Action.py` | Puzzle state, search node, and move representation |
| `Fringe.py`, `SearchAgent.py` | Priority-queue open set and the search loop that drives it |
| `Heuristic.py`, `HammingDistance.py`, `ManhattanDistance.py`, `ZeroHeuristic.py` | Heuristic interface and implementations |
| `NoSolutionError.py` | Raised when a puzzle has no solution reachable from the fringe |
| `tests/` | Unit tests (see [docs/TESTING.md](docs/TESTING.md)) |

For the full class/function reference and architecture diagrams, see
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Running the tests

```
pytest
```

See [docs/TESTING.md](docs/TESTING.md) for a per-module breakdown of what's
covered.

## Documentation index

- [docs/CONFIGURATION.md](docs/CONFIGURATION.md) — `config.ini` reference and available puzzle boards
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — class diagram, search workflow, and per-module reference
- [docs/SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md) — input → processing → output pipeline diagram
- [docs/ENVIRONMENT_MODEL.md](docs/ENVIRONMENT_MODEL.md) — `Problem` as the interface `SearchAgent` uses, built on foundational `Node`/`Action`
- [docs/AGENT_MODEL.md](docs/AGENT_MODEL.md) — `SearchAgent` as the main class, with `Fringe`/`Heuristic` as internal helpers
- [docs/APP_WORKFLOW.md](docs/APP_WORKFLOW.md) — `app.py`'s own control flow, start to finish
- [docs/SEARCH_ACTIVITY.md](docs/SEARCH_ACTIVITY.md) — class-interaction (sequence) diagram for `SearchAgent.search()`
- [docs/TESTING.md](docs/TESTING.md) — test suite reference
