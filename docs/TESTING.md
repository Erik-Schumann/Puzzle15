# Testing reference

Each module has a matching `tests/test_*.py` file, built on the
standard-library `unittest` framework (run via `pytest`, which is already
installed) — no extra dependency required. `conftest.py` at the project root
adds the root to `sys.path` so the `tests/` package can import the
root-level modules directly.

Run the full suite with either:

```
pytest
```

or:

```
python -m unittest discover -s tests -t . -p "test_*.py"
```

## `tests/test_action.py`

| Test | Description |
|---|---|
| `test_members_have_expected_values` | Each member's `.value` matches its lowercase direction name. |
| `test_has_exactly_four_members` | Only the four cardinal directions are defined. |

## `tests/test_no_solution_error.py`

| Test | Description |
|---|---|
| `test_is_an_exception_subclass` | `NoSolutionError` is a standard `Exception`, so it can be caught generically. |
| `test_carries_its_message` | The message passed at raise time is preserved on the exception. |

## `tests/test_heuristic.py`

| Test | Description |
|---|---|
| `test_cannot_be_instantiated_directly` | `Heuristic` itself has no concrete `get_heuristic`, so it can't be instantiated. |
| `test_subclass_must_implement_get_heuristic` | A subclass that skips `get_heuristic` is still abstract and can't be instantiated. |

## `tests/test_node.py`

| Test | Description |
|---|---|
| `test_init_stores_state_and_defaults` | A bare `Node` stores its state and defaults `action`/`predecessor`/`cost`. |
| `test_init_stores_explicit_action_predecessor_and_cost` | A successor `Node` stores the action, predecessor, and cost it was given. |
| `test_hash_depends_only_on_state` | Two nodes with the same state hash equal regardless of action/predecessor/cost. |
| `test_hash_differs_for_different_states` | Nodes with different board states hash differently. |
| `test_path_cost_returns_stored_cost` | `path_cost()` reads back the cost the node was constructed with. |
| `test_str_includes_action_and_board_values` | `str(node)` mentions the action taken and the board's tile values. |
| `test_str_reports_none_when_no_action` | `str(node)` reports `"None"` for the action on the root node. |
| `test_print_history_logs_ancestors_before_self` | `print_history()` logs the root node before its descendants, at `INFO` level. |

## `tests/test_problem.py`

| Test | Description |
|---|---|
| `test_init_wraps_initial_state_and_records_size` | The constructor wraps the given state as the initial node and records its size. |
| `test_is_goal_state_true_for_solved_board` | A board in row-major order with the blank last is the goal state. |
| `test_is_goal_state_false_for_unsolved_board` | Any board that doesn't match the solved layout is not a goal state. |
| `test_get_successors_from_corner_blank` | A blank in a corner can only move in the two directions that stay on the board. |
| `test_get_successors_from_middle_blank` | A blank with all four neighbors on the board yields four successors. |
| `test_get_successors_sets_predecessor_and_cost` | Every successor points back to its parent node with `cost = parent.cost + 1`. |
| `test_from_csv_builds_matching_problem` | A well-formed CSV file produces a `Problem` wrapping the matching board. |
| `test_from_csv_missing_file_raises_file_not_found_error` | A nonexistent path raises the standard `FileNotFoundError`. |
| `test_from_csv_non_square_grid_raises_value_error` | A CSV whose rows aren't all the same length as the row count raises `ValueError`. |
| `test_from_csv_duplicate_values_raise_value_error` | A CSV missing a required tile value raises `ValueError`. |
| `test_from_csv_non_integer_value_raises_value_error` | A CSV cell that isn't an integer raises `ValueError`. |

## `tests/test_fringe.py`

| Test | Description |
|---|---|
| `test_is_empty_initially_true` | A freshly created fringe holds nothing. |
| `test_push_pop_round_trips_a_single_node` | Pushing then popping a single node returns that same node. |
| `test_dijkstra_like_weights_order_purely_by_cost` | `a=1,b=0` orders purely by `g(n)`, regardless of push order (Dijkstra-equivalent). |
| `test_greedy_like_weights_order_purely_by_heuristic` | `a=0,b=1` orders purely by `h(n)`; a high-cost node can still pop first (Greedy-equivalent). |
| `test_push_without_heuristic_raises_type_error` | Pushing to a fringe with no heuristic set raises the standard `TypeError`. |
| `test_push_of_an_already_popped_state_is_skipped` | Pushing a node whose state was already popped is a no-op and reports `False`. |
| `test_pop_never_returns_the_same_state_twice` | Two fringe entries for the same state only yield that state once; the stale duplicate is silently discarded. |
| `test_pop_raises_no_solution_error_once_exhausted` | Popping an empty fringe raises `NoSolutionError`. |
| `test_default_weights_are_one` | With no weights given, `a` and `b` both default to `1` (plain A*). |
| `test_evaluation_applies_a_and_b_weights` | `f(n) = a*g(n) + b*h(n)` uses the given weights, not a plain sum. |
| `test_weighted_evaluation_can_change_pop_order` | A high `b` weight can make a farther-but-closer-to-goal node pop before a cheaper one. |
| `test_lowest_heuristic_starts_at_infinity` | Before anything is pushed, no heuristic has been observed yet. |
| `test_lowest_heuristic_tracks_the_minimum_seen` | `lowest_heuristic` tracks the smallest `h(n)` seen across all pushed nodes. |
| `test_lowest_heuristic_is_tracked_even_when_b_is_zero` | The heuristic is still evaluated (and tracked) even for a Dijkstra-equivalent `b=0`. |
| `test_max_fringe_size_starts_at_zero` | Before anything is pushed, the fringe has never held any nodes. |
| `test_max_fringe_size_tracks_the_peak_queue_size` | `max_fringe_size` tracks the largest the queue has grown to, not its current size after later pops. |
| `test_max_fringe_size_ignores_skipped_pushes` | Pushing an already-popped state doesn't grow the queue, so it isn't counted. |
| `test_track_visited_defaults_to_true` | With no argument given, visited-state tracking is enabled. |
| `test_disabling_track_visited_allows_pushing_an_already_popped_state` | With `track_visited=False`, a state already popped can be pushed again. |
| `test_disabling_track_visited_allows_popping_the_same_state_twice` | With `track_visited=False`, `pop()` doesn't dedupe stale duplicates by state. |

## `tests/test_hamming_distance.py`

| Test | Description |
|---|---|
| `test_goal_state_has_zero_misplaced_tiles` | The solved board has no misplaced tiles. |
| `test_single_swap_counts_two_misplaced_tiles` | Swapping two adjacent tiles misplaces exactly both of them. |
| `test_displaced_blank_counts_both_affected_cells` | Moving the blank out of place also misplaces the tile now sitting in its slot. |
| `test_works_for_a_2x2_board` | The heuristic is size-agnostic and works on a 2x2 board too. |

## `tests/test_manhattan_distance.py`

| Test | Description |
|---|---|
| `test_goal_state_has_zero_distance` | The solved board has zero total displacement. |
| `test_single_swap_of_adjacent_tiles_counts_two` | Swapping two adjacent tiles displaces each of them by one cell. |
| `test_blank_position_is_not_counted` | The blank itself contributes no distance; only the displaced tile does. |
| `test_works_for_a_2x2_board` | The heuristic is size-agnostic and works on a 2x2 board too. |

## `tests/test_zero_heuristic.py`

| Test | Description |
|---|---|
| `test_goal_state_returns_zero` | The solved board estimates zero, like every other state. |
| `test_scrambled_state_still_returns_zero` | A far-from-goal board also estimates zero, regardless of state. |
| `test_works_for_a_2x2_board` | The heuristic is size-agnostic and works on a 2x2 board too. |

## `tests/test_search_agent.py`

| Test | Description |
|---|---|
| `test_defaults_to_manhattan_heuristic_when_none_given` | No heuristic argument falls back to `ManhattanDistance`. |
| `test_defaults_to_unit_evaluation_weights` | No `a`/`b` arguments fall back to `a=1, b=1` (a plain, unweighted A*-like evaluation). |
| `test_forwards_evaluation_weights_to_the_fringe` | Custom `a`/`b` weights are stored and passed through to the underlying `Fringe`. |
| `test_defaults_log_interval_to_the_class_default` | No `log_interval` argument falls back to `DEFAULT_LOG_INTERVAL`. |
| `test_stores_a_custom_log_interval` | A given `log_interval` argument overrides the default. |
| `test_init_logs_the_agent_configuration` | The constructor logs its resulting configuration at `DEBUG` level. |
| `test_dijkstra_like_weights_find_the_optimal_path_cost` | `a=1,b=0` (uniform-cost search) finds the shortest path to the goal. |
| `test_greedy_like_weights_with_hamming_reach_the_goal` | `a=0,b=1` with the Hamming heuristic still reaches the goal. |
| `test_astar_like_weights_with_manhattan_find_the_optimal_path_cost` | `a=1,b=1` with the Manhattan heuristic finds the shortest path to the goal. |
| `test_search_raises_no_solution_error_for_unsolvable_board` | A board outside the goal's connected component raises `NoSolutionError`. |
| `test_search_logs_debug_progress_every_log_interval` | `search()` logs a `DEBUG` message every `log_interval` loop iterations. |
| `test_search_debug_log_reports_lowest_heuristic` | The `DEBUG` progress message includes the lowest heuristic value observed so far. |
| `test_search_debug_log_reports_evaluation` | The `DEBUG` progress message includes the current node's evaluation `f(n)`. |
| `test_search_debug_log_reports_max_fringe_size` | The `DEBUG` progress message includes the peak fringe size observed so far. |
| `test_max_fringe_size_property_reads_from_the_fringe` | The agent's `max_fringe_size` property proxies the underlying `Fringe`'s value. |
| `test_search_logs_info_when_goal_found` | `search()` logs an `INFO` message reporting the goal node's evaluation, heuristic, path cost, and peak fringe size. |
| `test_search_logs_goal_node_history` | `search()` logs the full path history once the goal node is found. |
| `test_defaults_track_visited_to_true` | No `track_visited` argument leaves visited-state tracking enabled on the fringe. |
| `test_forwards_track_visited_to_the_fringe` | `track_visited=False` is stored and passed through to the underlying `Fringe`. |
| `test_defaults_max_nodes_observed_and_max_fringe_size_to_none` | With no arguments given, neither search-effort limit is enforced. |
| `test_search_raises_no_solution_error_when_max_nodes_observed_is_exceeded` | Exceeding `max_nodes_observed` raises `NoSolutionError` naming that limit, even for an otherwise-solvable board. |
| `test_search_logs_warning_when_max_nodes_observed_is_exceeded` | `search()` logs a `WARNING` message before raising for an exceeded `max_nodes_observed`. |
| `test_search_raises_no_solution_error_when_max_fringe_size_is_exceeded` | Exceeding `max_fringe_size` raises `NoSolutionError` naming that limit, even for an otherwise-solvable board. |
| `test_search_logs_warning_when_max_fringe_size_is_exceeded` | `search()` logs a `WARNING` message before raising for an exceeded `max_fringe_size`. |
| `test_greedy_like_weights_solve_various_board_sizes` | `a=0,b=1` (Greedy) reaches the goal on 2x2 through 6x6 boards, confirming the search is generic in board size and not tied to 4x4. |

## `tests/test_app.py`

| Test | Description |
|---|---|
| `test_reads_a_valid_level_from_the_config_file` | A well-formed `[generalsettings] level` entry resolves to the matching `logging` constant. |
| `test_is_case_insensitive` | Lowercase level names resolve just like uppercase ones. |
| `test_falls_back_to_default_when_file_is_missing` *(level)* | A nonexistent config path falls back to `DEFAULT_LOG_LEVEL` instead of raising. |
| `test_falls_back_to_default_when_section_is_missing` *(level)* | A config file without a `[generalsettings]` section falls back to `DEFAULT_LOG_LEVEL`. |
| `test_falls_back_to_warning_for_an_unknown_level_name` | An unrecognized level name falls back to `WARNING` rather than raising. |
| `test_strips_trailing_inline_comments` | A trailing `# ...` comment after the value doesn't become part of it. |
| `test_reads_a_valid_interval_from_the_config_file` | A well-formed `[generalsettings] log_interval` entry resolves to that integer. |
| `test_falls_back_to_default_when_file_is_missing` *(interval)* | A nonexistent config path falls back to `DEFAULT_LOG_INTERVAL` instead of raising. |
| `test_falls_back_to_default_when_section_is_missing` *(interval)* | A config file without a `[generalsettings]` section falls back to `DEFAULT_LOG_INTERVAL`. |
| `test_falls_back_to_default_for_a_non_integer_value` | A non-integer value falls back to `DEFAULT_LOG_INTERVAL` rather than raising. |
| `test_falls_back_to_default_for_a_non_positive_value` | A zero or negative interval falls back to `DEFAULT_LOG_INTERVAL` (avoiding a `ZeroDivisionError` in `SearchAgent`). |
| `test_state_is_used_as_the_csv_path` | `[problem] state` is read back verbatim as the CSV path to load. |
| `test_falls_back_to_default_when_file_is_missing` *(csv path)* | A nonexistent config path falls back to `DEFAULT_CSV_PATH` instead of raising. |
| `test_falls_back_to_default_when_section_is_missing` *(csv path)* | A config file without a `[problem]` section falls back to `DEFAULT_CSV_PATH`. |
| `test_falls_back_to_default_when_state_is_empty` | An empty/unset `[problem] state` value falls back to `DEFAULT_CSV_PATH`. |
| `test_reads_a_well_formed_configuration_line` | A well-formed 3-field line resolves to `(label, heuristic instance, a, b, True)`. |
| `test_preserves_the_label_case_and_file_order` | Labels keep their original case, and entries come back in file order. |
| `test_blank_heuristic_means_no_heuristic` | A blank heuristic field (for a Dijkstra-equivalent `b=0`) resolves to a `None` heuristic. |
| `test_falls_back_to_default_when_file_is_missing` *(searchagents)* | A nonexistent config path resolves the same labels as `DEFAULT_CONFIGURATIONS`. |
| `test_falls_back_to_default_when_section_is_missing` *(searchagents)* | A config file without a `[searchagents]` section resolves `DEFAULT_CONFIGURATIONS`. |
| `test_skips_a_line_with_an_unknown_heuristic` | A line naming an unrecognized heuristic is skipped rather than raising. |
| `test_falls_back_to_default_when_every_line_is_invalid` | If every line fails to parse, falls back to `DEFAULT_CONFIGURATIONS` rather than silently running zero configurations. |
| `test_skips_a_line_with_non_numeric_weights` | A line with a non-numeric `a`/`b` is skipped rather than raising. |
| `test_defaults_track_visited_to_true_when_field_is_omitted` | A 3-field line (no `track_visited`) defaults that agent to `track_visited=True`. |
| `test_reads_an_explicit_true_track_visited_field` | A 4th field of `true` resolves that agent's `track_visited` to `True`. |
| `test_reads_an_explicit_false_track_visited_field` | A 4th field of `false` resolves that agent's `track_visited` to `False`. |
| `test_track_visited_is_independent_per_line` | Different lines can mix `track_visited=true` and `track_visited=false`. |
| `test_skips_a_line_with_an_unrecognized_track_visited_value` | A 4th field that isn't a recognized boolean is skipped rather than raising. |
| `test_skips_a_line_with_the_wrong_number_of_fields` | A line with fewer than 3 or more than 4 fields is skipped rather than raising. |
| `test_reads_a_valid_limit_from_the_config_file` *(max_nodes_observed)* | A well-formed `max_nodes_observed` entry resolves to that integer. |
| `test_falls_back_to_none_when_file_is_missing` *(max_nodes_observed)* | A nonexistent config path falls back to `None` (no limit) instead of raising. |
| `test_falls_back_to_none_when_key_is_blank` *(max_nodes_observed)* | A blank value falls back to `None` (no limit) rather than raising. |
| `test_falls_back_to_none_for_a_non_positive_value` *(max_nodes_observed)* | A zero or negative limit falls back to `None` (no limit) rather than raising. |
| `test_falls_back_to_none_for_a_non_integer_value` *(max_nodes_observed)* | A non-integer value falls back to `None` (no limit) rather than raising. |
| `test_reads_a_valid_limit_from_the_config_file` *(max_fringe_size)* | A well-formed `max_fringe_size` entry resolves to that integer. |
| `test_falls_back_to_none_when_file_is_missing` *(max_fringe_size)* | A nonexistent config path falls back to `None` (no limit) instead of raising. |
| `test_falls_back_to_none_when_key_is_blank` *(max_fringe_size)* | A blank value falls back to `None` (no limit) rather than raising. |
| `test_falls_back_to_none_for_a_non_positive_value` *(max_fringe_size)* | A zero or negative limit falls back to `None` (no limit) rather than raising. |
| `test_falls_back_to_none_for_a_non_integer_value` *(max_fringe_size)* | A non-integer value falls back to `None` (no limit) rather than raising. |
| `test_returns_none_and_writes_nothing_for_empty_results` | With no solved configurations, there's nothing to chart. |
| `test_writes_a_chart_file_and_returns_its_path` | A non-empty results list is rendered to `output_path` and that path is returned. |
| `test_handles_a_single_result` | A single solved configuration still renders without error. |
