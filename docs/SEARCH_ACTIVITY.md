# Search activity: class interaction for `SearchAgent.search()`

While the "Search workflow" flowchart in [ARCHITECTURE.md](ARCHITECTURE.md#search-workflow)
shows the *control flow* of one `search()` call, this diagram shows the same
call as an **activity/interaction diagram between classes** — which object
sends which message to which other object, in order.

Participants:

| Participant | Class | Role |
|---|---|---|
| `App` | `app.py` | Caller; owns the loop over configurations. |
| `SA` | `SearchAgent` | Drives the search loop. |
| `FR` | `Fringe` | Priority-queue open set; evaluates and orders nodes. |
| `PR` | `Problem` | Goal test and successor generation. |
| `HE` | `Heuristic` | `HammingDistance`, `ManhattanDistance`, or `ZeroHeuristic`; estimates `h(n)`. |
| `ND` | `Node` | A single board state plus the action/predecessor/cost that produced it. |

```mermaid
sequenceDiagram
    participant App as app.py
    participant SA as SearchAgent
    participant FR as Fringe
    participant PR as Problem
    participant HE as Heuristic
    participant ND as Node

    App->>SA: search(problem)
    SA->>PR: get_initial_node()
    PR-->>SA: initial Node
    SA->>FR: push(initial node)
    FR->>HE: get_heuristic(node)
    HE-->>FR: h(n)
    Note over FR: priority = a*g(n) + b*h(n)<br/>update lowest_heuristic<br/>update max_fringe_size from queue size
    FR-->>SA: True (inserted)

    loop until goal found, fringe exhausted, or a limit is exceeded
        SA->>FR: pop()
        alt fringe exhausted
            FR-->>SA: raise NoSolutionError
            SA-->>App: propagate NoSolutionError
        else node available
            FR-->>SA: next Node<br/>(next not-yet-visited one, if track_visited)
        end
        Note over SA: nodes_observed += 1
        alt max_nodes_observed set and exceeded
            Note over SA: logger.warning(...)
            SA-->>App: raise NoSolutionError
        end
        opt nodes_observed % log_interval == 0
            SA->>FR: _evaluate(node)
            FR-->>SA: f(n)
            Note over SA: logger.debug(observed, inserted, lowest_heuristic,<br/>evaluation, max_fringe_size)
        end
        SA->>PR: is_goal_state(node)
        PR-->>SA: bool
        alt goal reached
            SA->>FR: _evaluate(node)
            FR-->>SA: f(n)
            SA->>HE: get_heuristic(node)
            HE-->>SA: h(n)
            Note over SA: logger.info(Goal state found:<br/>evaluation, heuristic, path_cost, max_fringe_size)
            SA->>ND: print_history()
            SA-->>App: return goal Node
        else not goal
            SA->>PR: get_successors(node)
            PR->>ND: Node(new_state, action, node, cost + 1)
            ND-->>PR: child Node
            PR-->>SA: list of successor Nodes
            loop for each child
                SA->>FR: push(child)
                Note over FR: track_visited and hash(child) already visited?
                alt already visited (and track_visited enabled)
                    FR-->>SA: False (skipped)
                else new state (or track_visited disabled)
                    FR->>HE: get_heuristic(child)
                    HE-->>FR: h(n)
                    Note over FR: priority = a*g(n) + b*h(n)<br/>update lowest_heuristic<br/>update max_fringe_size from queue size
                    FR-->>SA: True (inserted)
                    Note over SA: nodes_inserted += 1
                    alt max_fringe_size set and exceeded
                        Note over SA: logger.warning(...)
                        SA-->>App: raise NoSolutionError
                    end
                end
            end
        end
    end
```

## Reading this against the flowchart

Both diagrams describe the same call; they answer different questions:

- [ARCHITECTURE.md](ARCHITECTURE.md#search-workflow)'s flowchart — "what
  branch does execution take next?" (loop-exit conditions, goal test,
  log-interval check).
- This diagram — "which class asked which other class to do something?"
  (during the main loop, `SearchAgent` never computes a heuristic itself; it
  goes through `Fringe`, which is the only class that talks to `Heuristic`
  during node evaluation).

Every `Node` is constructed by `Problem` (the initial one in
`get_initial_node`, successors in `get_successors`); `SearchAgent` only ever
holds references to the ones `Problem`/`Fringe` hand it. The one exception is
the goal node: once found, `SearchAgent` calls `Heuristic.get_heuristic` and
`Node.print_history` on it directly to report the result, rather than going
through `Fringe`/`Problem`.

See [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) for where this call fits
in the overall input → processing → output pipeline, and
[AGENT_MODEL.md](AGENT_MODEL.md) for why `Fringe`/`Heuristic` are internal
helpers to `SearchAgent` rather than something callers use directly.
