"""Unit tests for Fringe."""

import unittest

from Fringe import Fringe
from HammingDistance import HammingDistance
from ManhattanDistance import ManhattanDistance
from NoSolutionError import NoSolutionError
from Node import Node


class TestFringe(unittest.TestCase):
    """Tests for Fringe's push/pop ordering and visited-state tracking."""

    def test_is_empty_initially_true(self):
        """A freshly created fringe holds nothing."""
        fringe = Fringe(ManhattanDistance())
        self.assertTrue(fringe.is_empty())

    def test_push_pop_round_trips_a_single_node(self):
        """Pushing then popping a single node returns that same node."""
        fringe = Fringe(ManhattanDistance())
        node = Node([[1, 2], [3, 0]])
        self.assertTrue(fringe.push(node))
        self.assertFalse(fringe.is_empty())
        self.assertIs(fringe.pop(), node)
        self.assertTrue(fringe.is_empty())

    def test_dijkstra_like_weights_order_purely_by_cost(self):
        """a=1,b=0 orders purely by g(n), regardless of push order (Dijkstra-equivalent)."""
        fringe = Fringe(ManhattanDistance(), a=1, b=0)
        cheap = Node([[1, 2], [3, 0]], cost=1)
        expensive = Node([[0, 2], [3, 1]], cost=9)
        fringe.push(expensive)
        fringe.push(cheap)
        self.assertIs(fringe.pop(), cheap)
        self.assertIs(fringe.pop(), expensive)

    def test_greedy_like_weights_order_purely_by_heuristic(self):
        """a=0,b=1 orders purely by h(n); a high-cost node can still pop first (Greedy-equivalent)."""
        fringe = Fringe(HammingDistance(), a=0, b=1)
        near_goal = Node([[1, 2], [3, 0]], cost=100)  # hamming = 0
        far_from_goal = Node([[0, 2], [3, 1]], cost=0)  # hamming = 2
        fringe.push(far_from_goal)
        fringe.push(near_goal)
        self.assertIs(fringe.pop(), near_goal)

    def test_push_without_heuristic_raises_type_error(self):
        """Pushing to a fringe with no heuristic set raises the standard TypeError."""
        fringe = Fringe(None)
        with self.assertRaises(TypeError):
            fringe.push(Node([[1, 2], [3, 0]]))

    def test_push_of_an_already_popped_state_is_skipped(self):
        """Pushing a node whose state was already popped is a no-op and reports False."""
        fringe = Fringe(ManhattanDistance())
        fringe.push(Node([[1, 2], [3, 0]], cost=1))
        fringe.pop()

        self.assertFalse(fringe.push(Node([[1, 2], [3, 0]], cost=5)))
        self.assertTrue(fringe.is_empty())

    def test_pop_never_returns_the_same_state_twice(self):
        """Two fringe entries for the same state (pushed before either was popped)
        only yield that state once; the stale duplicate is silently discarded."""
        fringe = Fringe(ManhattanDistance())
        first_copy = Node([[1, 2], [3, 0]], cost=1)
        second_copy = Node([[1, 2], [3, 0]], cost=1)
        other = Node([[0, 2], [3, 1]], cost=1)

        fringe.push(first_copy)
        fringe.push(second_copy)
        fringe.push(other)

        popped = [fringe.pop(), fringe.pop()]
        self.assertIn(first_copy, popped)
        self.assertIn(other, popped)
        self.assertTrue(fringe.is_empty())

    def test_pop_raises_no_solution_error_once_exhausted(self):
        """Popping an empty fringe raises NoSolutionError."""
        fringe = Fringe(ManhattanDistance())
        with self.assertRaises(NoSolutionError):
            fringe.pop()

    def test_default_weights_are_one(self):
        """With no weights given, a and b both default to 1 (plain A*)."""
        fringe = Fringe(ManhattanDistance())
        self.assertEqual(fringe.a, 1.0)
        self.assertEqual(fringe.b, 1.0)

    def test_evaluation_applies_a_and_b_weights(self):
        """f(n) = a*g(n) + b*h(n) uses the given weights, not a plain sum."""
        fringe = Fringe(ManhattanDistance(), a=2, b=3)
        node = Node([[0, 2], [3, 1]], cost=5)  # manhattan distance = 2
        self.assertEqual(fringe._evaluate(node), 2 * 5 + 3 * 2)

    def test_weighted_evaluation_can_change_pop_order(self):
        """A high b weight can make a farther-but-closer-to-goal node pop before a cheaper one."""
        fringe = Fringe(ManhattanDistance(), a=1, b=5)
        cheap_but_far = Node([[0, 2], [3, 1]], cost=1)  # f = 1*1 + 5*2 = 11
        pricier_but_close = Node([[1, 2], [3, 0]], cost=3)  # f = 1*3 + 5*0 = 3
        fringe.push(cheap_but_far)
        fringe.push(pricier_but_close)
        self.assertIs(fringe.pop(), pricier_but_close)

    def test_lowest_heuristic_starts_at_infinity(self):
        """Before anything is pushed, no heuristic has been observed yet."""
        fringe = Fringe(ManhattanDistance())
        self.assertEqual(fringe.lowest_heuristic, float("inf"))

    def test_lowest_heuristic_tracks_the_minimum_seen(self):
        """lowest_heuristic tracks the smallest h(n) seen across all pushed nodes."""
        fringe = Fringe(ManhattanDistance())
        fringe.push(Node([[0, 2], [3, 1]]))  # manhattan distance = 2
        fringe.push(Node([[1, 2], [3, 0]]))  # manhattan distance = 0 (goal)
        self.assertEqual(fringe.lowest_heuristic, 0)

    def test_lowest_heuristic_is_tracked_even_when_b_is_zero(self):
        """The heuristic is still evaluated (and tracked) even for a Dijkstra-equivalent b=0."""
        fringe = Fringe(ManhattanDistance(), a=1, b=0)
        fringe.push(Node([[0, 2], [3, 1]], cost=1))  # manhattan distance = 2
        self.assertEqual(fringe.lowest_heuristic, 2)

    def test_max_fringe_size_starts_at_zero(self):
        """Before anything is pushed, the fringe has never held any nodes."""
        fringe = Fringe(ManhattanDistance())
        self.assertEqual(fringe.max_fringe_size, 0)

    def test_max_fringe_size_tracks_the_peak_queue_size(self):
        """max_fringe_size tracks the largest the queue has grown to, not its current size."""
        fringe = Fringe(ManhattanDistance())
        fringe.push(Node([[0, 2], [3, 1]], cost=1))
        fringe.push(Node([[2, 0], [3, 1]], cost=1))
        fringe.push(Node([[2, 1], [3, 0]], cost=1))
        self.assertEqual(fringe.max_fringe_size, 3)

        fringe.pop()
        self.assertEqual(fringe.max_fringe_size, 3)

    def test_max_fringe_size_ignores_skipped_pushes(self):
        """Pushing an already-popped state doesn't grow the queue, so it isn't counted."""
        fringe = Fringe(ManhattanDistance())
        fringe.push(Node([[1, 2], [3, 0]], cost=1))
        fringe.pop()

        fringe.push(Node([[1, 2], [3, 0]], cost=5))  # skipped: state already popped
        self.assertEqual(fringe.max_fringe_size, 1)

    def test_track_visited_defaults_to_true(self):
        """With no argument given, visited-state tracking is enabled."""
        fringe = Fringe(ManhattanDistance())
        self.assertTrue(fringe.track_visited)

    def test_disabling_track_visited_allows_pushing_an_already_popped_state(self):
        """With track_visited=False, a state already popped can be pushed again."""
        fringe = Fringe(ManhattanDistance(), track_visited=False)
        fringe.push(Node([[1, 2], [3, 0]], cost=1))
        fringe.pop()

        self.assertTrue(fringe.push(Node([[1, 2], [3, 0]], cost=5)))

    def test_disabling_track_visited_allows_popping_the_same_state_twice(self):
        """With track_visited=False, pop() doesn't dedupe stale duplicates by state."""
        fringe = Fringe(ManhattanDistance(), track_visited=False)
        first_copy = Node([[1, 2], [3, 0]], cost=1)
        second_copy = Node([[1, 2], [3, 0]], cost=1)

        fringe.push(first_copy)
        fringe.push(second_copy)

        popped = [fringe.pop(), fringe.pop()]
        self.assertIn(first_copy, popped)
        self.assertIn(second_copy, popped)


if __name__ == "__main__":
    unittest.main()
