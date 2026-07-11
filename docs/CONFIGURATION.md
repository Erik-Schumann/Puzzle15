# Configuration reference

Everything about a run — which puzzle to solve, which search configurations
to try, and how much to log — is controlled by
[`input/config.ini`](../input/config.ini).

## `input/config.ini`

```ini
[generalsettings]
level = DEBUG
log_interval = 50000
max_nodes_observed =
max_fringe_size =

[problem]
state = input/state_30.csv

[searchagents]
# label = heuristic, a, b
# label = heuristic, a, b, track_visited
# heuristic: hamming, manhattan, or zero (leave blank to use SearchAgent's default).
# a/b weight the evaluation function as f(n) = a*g(n) + b*h(n).
# a=1,b=0 behaves like Dijkstra; a=0,b=1 like Greedy; a=1,b=1 like plain A*.
Greedy (Hamming) = hamming, 0, 1
Greedy (Manhattan) = manhattan, 0, 1
A* (Hamming) = hamming, 1, 1
A* (Manhattan) = manhattan, 1, 1
Greedy (Manhattan, tree search) = manhattan, 0, 1, false
; Dijkstra = , 1, 0
```

### `[generalsettings]`

| Key | Meaning | Default if missing/invalid |
|---|---|---|
| `level` | Console log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, ...). Controls whether `SearchAgent`'s periodic `DEBUG` progress messages show up, and whether its `INFO`-level "goal state found" message (evaluation, heuristic, path cost) shows up. | `WARNING` |
| `log_interval` | How many search-loop iterations pass between those `DEBUG` progress messages. | `SearchAgent.DEFAULT_LOG_INTERVAL` (`50_000`) |
| `max_nodes_observed` | Upper limit on how many nodes `SearchAgent.search()` may pop from the fringe. Once exceeded, `search()` logs a `WARNING` message naming the limit and raises `NoSolutionError` with a matching message, even if the board is solvable. Leave blank/unset for no limit. | No limit (`None`) |
| `max_fringe_size` | Upper limit on the fringe's peak size (`Fringe.max_fringe_size`). Once exceeded, `search()` logs a `WARNING` message naming the limit and raises `NoSolutionError` with a matching message, even if the board is solvable. Leave blank/unset for no limit. | No limit (`None`) |

Both limits are a safety valve for runs that would otherwise search (near-)indefinitely — e.g. Dijkstra/uniform-cost search on a deeply scrambled board — by turning an impractically long search into a prompt, diagnosable failure instead.

### `[problem]`

| Key | Meaning | Default if missing/empty |
|---|---|---|
| `state` | Path to the puzzle CSV to load. See [Puzzle boards](#puzzle-boards-input) below. | `input/state_custom.csv` |

### `[searchagents]`

One `SearchAgent` setup per line, in the form:

```
label = heuristic, a, b
label = heuristic, a, b, track_visited
```

- `heuristic` — `hamming`, `manhattan`, or `zero` (case-insensitive), or left
  blank to use `SearchAgent`'s own default (`ManhattanDistance`). `zero`
  always estimates 0, so `f(n)` depends only on `g(n)` regardless of `b`.
- `a`, `b` — weights for the evaluation function `f(n) = a*g(n) + b*h(n)`,
  where `g(n)` is the path cost so far and `h(n)` is the heuristic estimate
  to the goal.
- `track_visited` *(optional, per line, defaults to `true` if omitted)* —
  whether that agent's `Fringe` remembers and skips already-popped states, so
  no state is ever explored twice (`true`), or allows the same state to be
  pushed/popped more than once (`false`). Recognizes the same true/false
  spellings as `ConfigParser.getboolean` (`true`/`false`, `yes`/`no`,
  `on`/`off`, `1`/`0`, case-insensitive). Disabling it turns graph search into
  tree search for that one line — useful for comparing search behavior, but
  it can make that run much slower or non-terminating on boards with cycles.
  Since it's per line, different configurations in the same run can mix
  `track_visited=true` and `track_visited=false`.

Common weight combinations:

| `a` | `b` | Behaves like |
|---|---|---|
| `1` | `0` | Dijkstra / uniform-cost search |
| `0` | `1` | Greedy best-first search |
| `1` | `1` | Plain A* |
| `1` | `>1` | Weighted A* (faster, no longer guaranteed optimal) |

Each line is independent, so different lines can mix different heuristics and
weights in the same run — `app.py` runs every configured line against the
same puzzle and reports/plots them side by side.

If the `[searchagents]` section is missing, empty, or every line in it
fails to parse, the run falls back to a built-in default (Greedy and A* with
each heuristic, all with `track_visited=true`). A line with the wrong number
of fields (fewer than 3 or more than 4), a bad heuristic name, non-numeric
`a`/`b`, or an unrecognized `track_visited` value is skipped (with a warning
printed) rather than aborting the whole run.

**Gotcha:** labels can't contain `=` or `:`. `ConfigParser` splits each line
on the *first* occurrence of either character to separate the key from the
value, so a label like `Greedy (a=1)` would be parsed as key `Greedy (a` with
a garbled value.

### Comments

Trailing `# ...`/`; ...` text on a line is treated as an inline comment and
stripped. A full line starting with `#` or `;` (like the commented-out
`Dijkstra` line above) is skipped entirely — handy for keeping alternative
configurations around without deleting them.

**Gotcha:** an inline `#`/`;` comment must be preceded by whitespace, or
`ConfigParser` doesn't recognize it as a comment at all and includes it as
part of the value. For example `max_fringe_size = 3500000#comment` resolves
to the literal string `"3500000#comment"`, not the integer `3500000` — for
`max_nodes_observed`/`max_fringe_size` this fails `int()` conversion and
silently falls back to *no limit*, rather than raising. Always leave a space
before the comment character: `3500000 # comment`.

## Puzzle boards (`input/`)

Puzzle-board CSVs, each a `size`-row grid of comma-separated tile values (`0`
= blank). Point `[problem] state` in `input/config.ini` at whichever one you
want to solve, or supply your own CSV in the same format.

| File | Verified optimal solution length |
|---|---|
| `state_custom.csv` | 48 moves (deeply scrambled; this is the default board if `state` is unset) |
| `state_10.csv` | 10 moves |
| `state_20.csv` | 20 moves |
| `state_30.csv` | 30 moves |
| `state_40.csv` | 40 moves |

The four `state_N.csv` boards were generated by taking `N` random
non-backtracking moves from the solved board, then verifying with A*/Manhattan
that the true optimal solution is exactly `N` moves (retrying with different
random seeds until an exact match was found). A fifth, `state_50.csv`, was
attempted the same way but no seed within a reasonable search budget produced
an exact 50-move optimum (results clustered in the 30s-40s instead, since
longer random walks are increasingly likely to contain redundant loops that
shorten the true optimal path) — so it was dropped rather than shipped
mislabeled.

Loading a board is validated by `Problem.from_csv`, which raises
`FileNotFoundError` if the path doesn't exist, and `ValueError` if the CSV
isn't a square grid or doesn't contain each value `0..size*size-1` exactly
once.

## Output

Each run logs one summary line per configuration (moves, elapsed time,
nodes observed, nodes inserted, max fringe size), or the `NoSolutionError`
message if that configuration's board has no solution reachable from the
fringe *or* if `max_nodes_observed`/`max_fringe_size` was exceeded first (the
message names which limit was hit). It then writes `output/comparison.png` (the directory is created
automatically if it doesn't exist): a 2x3 grid of horizontal-bar
subplots (moves, time, nodes observed, nodes inserted, max fringe size; the
sixth cell is left blank), one bar per solved configuration, in the order
they appear in `input/config.ini`. Configurations that raised
`NoSolutionError` are excluded from the chart.
