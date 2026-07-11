"""Unit tests for SearchAgent."""

import unittest

from HammingDistance import HammingDistance
from ManhattanDistance import ManhattanDistance
from NoSolutionError import NoSolutionError
from Problem import Problem
from SearchAgent import SearchAgent


def _scrambled_state(size, num_moves):
    """Build a size x size board reached from the solved state by `num_moves` legal slides.

    Since every move is a legal blank-slide starting from the goal, the result is
    guaranteed solvable regardless of `size`, without needing a size-specific fixture.
    Direction is cycled (up, right, down, left), skipping moves that would leave the
    board, so the same deterministic scramble logic works for any board size.
    """
    state = [[row * size + col + 1 for col in range(size)] for row in range(size)]
    state[size - 1][size - 1] = 0
    row, col = size - 1, size - 1

    direction_cycle = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    applied = 0
    step = 0
    while applied < num_moves:
        delta_row, delta_col = direction_cycle[step % len(direction_cycle)]
        next_row, next_col = row + delta_row, col + delta_col
        if 0 <= next_row < size and 0 <= next_col < size:
            state[row][col], state[next_row][next_col] = state[next_row][next_col], state[row][col]
            row, col = next_row, next_col
            applied += 1
        step += 1

    return state


class TestSearchAgent(unittest.TestCase):
    """End-to-end tests for SearchAgent, including its Dijkstra/Greedy/A*-equivalent weightings."""

    def test_defaults_to_manhattan_heuristic_when_none_given(self):
        """No heuristic argument falls back to ManhattanDistance."""
        agent = SearchAgent()
        self.assertIsInstance(agent.heuristic, ManhattanDistance)

    def test_defaults_to_unit_evaluation_weights(self):
        """No a/b arguments fall back to a=1, b=1 (a plain, unweighted A*-like evaluation)."""
        agent = SearchAgent()
        self.assertEqual(agent.a, 1.0)
        self.assertEqual(agent.b, 1.0)

    def test_forwards_evaluation_weights_to_the_fringe(self):
        """Custom a/b weights are stored and passed through to the underlying Fringe."""
        agent = SearchAgent(a=1, b=5)
        self.assertEqual(agent.a, 1)
        self.assertEqual(agent.b, 5)
        self.assertEqual(agent.fringe.a, 1)
        self.assertEqual(agent.fringe.b, 5)

    def test_defaults_log_interval_to_the_class_default(self):
        """No log_interval argument falls back to DEFAULT_LOG_INTERVAL."""
        agent = SearchAgent()
        self.assertEqual(agent.log_interval, SearchAgent.DEFAULT_LOG_INTERVAL)

    def test_stores_a_custom_log_interval(self):
        """A given log_interval argument overrides the default."""
        agent = SearchAgent(log_interval=100)
        self.assertEqual(agent.log_interval, 100)

    def test_init_logs_the_agent_configuration(self):
        """The constructor logs its resulting configuration at DEBUG level."""
        with self.assertLogs("SearchAgent", level="DEBUG") as log_context:
            SearchAgent(HammingDistance(), a=1, b=5)

        message = log_context.output[0]
        self.assertIn("SearchAgent created", message)
        self.assertIn("HammingDistance", message)

    def test_dijkstra_like_weights_find_the_optimal_path_cost(self):
        """a=1,b=0 (uniform-cost search) finds the shortest path to the goal."""
        problem = Problem([[1, 0], [3, 2]])  # one move away from solved
        agent = SearchAgent(a=1, b=0)
        goal_node = agent.search(problem)
        self.assertTrue(problem.is_goal_state(goal_node))
        self.assertEqual(goal_node.path_cost(), 1)

    def test_greedy_like_weights_with_hamming_reach_the_goal(self):
        """a=0,b=1 with the Hamming heuristic still reaches the goal."""
        problem = Problem([[1, 0], [3, 2]])
        agent = SearchAgent(HammingDistance(), a=0, b=1)
        goal_node = agent.search(problem)
        self.assertTrue(problem.is_goal_state(goal_node))

    def test_greedy_like_weights_solve_various_board_sizes(self):
        """a=0,b=1 (Greedy) reaches the goal on 2x2 through 6x6 boards, not just 4x4.

        Confirms the search itself is generic in board size (Problem/heuristics
        already derive their dimensions from the input, see Problem.get_successors
        and ManhattanDistance.get_heuristic) by actually solving one board of each
        size rather than just asserting on shapes.
        """
        scramble_depth_by_size = {2: 3, 3: 6, 4: 8, 5: 10, 6: 12}

        for size, num_moves in scramble_depth_by_size.items():
            with self.subTest(size=size):
                problem = Problem(_scrambled_state(size, num_moves))
                agent = SearchAgent(ManhattanDistance(), a=0, b=1, max_nodes_observed=200_000)

                goal_node = agent.search(problem)

                self.assertTrue(problem.is_goal_state(goal_node))

    def test_astar_like_weights_with_manhattan_find_the_optimal_path_cost(self):
        """a=1,b=1 with the Manhattan heuristic finds the shortest path to the goal."""
        problem = Problem([[1, 0], [3, 2]])
        agent = SearchAgent(ManhattanDistance(), a=1, b=1)
        goal_node = agent.search(problem)
        self.assertEqual(goal_node.path_cost(), 1)

    def test_search_raises_no_solution_error_for_unsolvable_board(self):
        """A board outside the goal's connected component raises NoSolutionError."""
        # Unreachable from [[1, 2], [3, 0]]: verified via BFS over the full state space.
        problem = Problem([[2, 0], [3, 1]])
        agent = SearchAgent(a=1, b=0)
        with self.assertRaises(NoSolutionError):
            agent.search(problem)

    def test_search_logs_debug_progress_every_log_interval(self):
        """search() logs a DEBUG message every log_interval loop iterations."""
        problem = Problem([[1, 0], [3, 2]])
        # log_interval=1 logs on every iteration so a short search still triggers it.
        agent = SearchAgent(a=1, b=0, log_interval=1)

        with self.assertLogs("SearchAgent", level="DEBUG") as log_context:
            agent.search(problem)

        self.assertTrue(any("nodes observed" in message for message in log_context.output))

    def test_search_debug_log_reports_lowest_heuristic(self):
        """The DEBUG progress message includes the lowest heuristic value observed so far."""
        problem = Problem([[1, 0], [3, 2]])
        agent = SearchAgent(ManhattanDistance(), log_interval=1)

        with self.assertLogs("SearchAgent", level="DEBUG") as log_context:
            agent.search(problem)

        self.assertTrue(any("lowest heuristic" in message for message in log_context.output))

    def test_search_debug_log_reports_evaluation(self):
        """The DEBUG progress message includes the current node's evaluation f(n)."""
        problem = Problem([[1, 0], [3, 2]])
        agent = SearchAgent(ManhattanDistance(), log_interval=1)

        with self.assertLogs("SearchAgent", level="DEBUG") as log_context:
            agent.search(problem)

        self.assertTrue(any("evaluation" in message for message in log_context.output))

    def test_search_debug_log_reports_max_fringe_size(self):
        """The DEBUG progress message includes the peak fringe size observed so far."""
        problem = Problem([[1, 0], [3, 2]])
        agent = SearchAgent(ManhattanDistance(), log_interval=1)

        with self.assertLogs("SearchAgent", level="DEBUG") as log_context:
            agent.search(problem)

        self.assertTrue(any("max fringe size" in message for message in log_context.output))

    def test_max_fringe_size_property_reads_from_the_fringe(self):
        """The agent's max_fringe_size property proxies the underlying Fringe's value."""
        problem = Problem([[1, 0], [3, 2]])
        agent = SearchAgent(ManhattanDistance())
        agent.search(problem)

        self.assertEqual(agent.max_fringe_size, agent.fringe.max_fringe_size)
        self.assertGreater(agent.max_fringe_size, 0)

    def test_search_logs_info_when_goal_found(self):
        """search() logs an INFO message reporting the goal node's evaluation, heuristic, path cost,
        and peak fringe size."""
        problem = Problem([[1, 0], [3, 2]])
        agent = SearchAgent(ManhattanDistance(), a=1, b=1)

        with self.assertLogs("SearchAgent", level="INFO") as log_context:
            agent.search(problem)

        message = log_context.output[0]
        self.assertIn("Goal state found", message)
        self.assertIn("evaluation", message)
        self.assertIn("heuristic", message)
        self.assertIn("path_cost", message)
        self.assertIn("max_fringe_size", message)

    def test_search_logs_goal_node_history(self):
        """search() logs the full path history once the goal node is found."""
        problem = Problem([[1, 0], [3, 2]])
        agent = SearchAgent(ManhattanDistance())

        with self.assertLogs("Node", level="INFO") as log_context:
            agent.search(problem)

        self.assertTrue(any("Action:" in message for message in log_context.output))

    def test_defaults_track_visited_to_true(self):
        """No track_visited argument leaves visited-state tracking enabled on the fringe."""
        agent = SearchAgent()
        self.assertTrue(agent.track_visited)
        self.assertTrue(agent.fringe.track_visited)

    def test_forwards_track_visited_to_the_fringe(self):
        """track_visited=False is stored and passed through to the underlying Fringe."""
        agent = SearchAgent(track_visited=False)
        self.assertFalse(agent.track_visited)
        self.assertFalse(agent.fringe.track_visited)

    def test_defaults_max_nodes_observed_and_max_fringe_size_to_none(self):
        """With no arguments given, neither search-effort limit is enforced."""
        agent = SearchAgent()
        self.assertIsNone(agent.max_nodes_observed)
        self.assertIsNone(agent.max_fringe_size_limit)

    def test_search_raises_no_solution_error_when_max_nodes_observed_is_exceeded(self):
        """Exceeding max_nodes_observed raises NoSolutionError naming that limit, even
        for an otherwise-solvable board."""
        problem = Problem([[1, 0], [3, 2]])
        agent = SearchAgent(max_nodes_observed=1)

        with self.assertRaises(NoSolutionError) as error_context:
            agent.search(problem)

        self.assertIn("1", str(error_context.exception))

    def test_search_logs_warning_when_max_nodes_observed_is_exceeded(self):
        """search() logs a WARNING message before raising for an exceeded max_nodes_observed."""
        problem = Problem([[1, 0], [3, 2]])
        agent = SearchAgent(max_nodes_observed=1)

        with self.assertLogs("SearchAgent", level="WARNING") as log_context:
            with self.assertRaises(NoSolutionError):
                agent.search(problem)

        self.assertTrue(any("nodes" in message for message in log_context.output))

    def test_search_raises_no_solution_error_when_max_fringe_size_is_exceeded(self):
        """Exceeding max_fringe_size raises NoSolutionError naming that limit, even
        for an otherwise-solvable board."""
        problem = Problem([[1, 0], [3, 2]])
        agent = SearchAgent(max_fringe_size=1)

        with self.assertRaises(NoSolutionError) as error_context:
            agent.search(problem)

        self.assertIn("1", str(error_context.exception))

    def test_search_logs_warning_when_max_fringe_size_is_exceeded(self):
        """search() logs a WARNING message before raising for an exceeded max_fringe_size."""
        problem = Problem([[1, 0], [3, 2]])
        agent = SearchAgent(max_fringe_size=1)

        with self.assertLogs("SearchAgent", level="WARNING") as log_context:
            with self.assertRaises(NoSolutionError):
                agent.search(problem)

        self.assertTrue(any("fringe size" in message for message in log_context.output))


if __name__ == "__main__":
    unittest.main()
