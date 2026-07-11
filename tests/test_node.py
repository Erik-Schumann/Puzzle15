"""Unit tests for Node."""

import unittest

from Action import Action
from Node import Node


class TestNode(unittest.TestCase):
    """Tests for Node's construction, hashing, cost, and printing."""

    def test_init_stores_state_and_defaults(self):
        """A bare Node stores its state and defaults action/predecessor/cost."""
        state = [[1, 2], [3, 0]]
        node = Node(state)
        self.assertEqual(node.state, state)
        self.assertIsNone(node.action)
        self.assertIsNone(node.predecessor)
        self.assertEqual(node.cost, 0)

    def test_init_stores_explicit_action_predecessor_and_cost(self):
        """A successor Node stores the action, predecessor, and cost it was given."""
        root = Node([[1, 2], [3, 0]])
        child = Node([[1, 2], [0, 3]], Action.LEFT, root, root.cost + 1)
        self.assertIs(child.predecessor, root)
        self.assertEqual(child.action, Action.LEFT)
        self.assertEqual(child.cost, 1)

    def test_hash_depends_only_on_state(self):
        """Two nodes with the same state hash equal regardless of action/predecessor/cost."""
        node_a = Node([[1, 2], [3, 0]], Action.UP, None, 5)
        node_b = Node([[1, 2], [3, 0]])
        self.assertEqual(hash(node_a), hash(node_b))

    def test_hash_differs_for_different_states(self):
        """Nodes with different board states hash differently."""
        node_a = Node([[1, 2], [3, 0]])
        node_b = Node([[2, 1], [3, 0]])
        self.assertNotEqual(hash(node_a), hash(node_b))

    def test_path_cost_returns_stored_cost(self):
        """path_cost() reads back the cost the node was constructed with."""
        node = Node([[1, 2], [3, 0]], cost=7)
        self.assertEqual(node.path_cost(), 7)

    def test_str_includes_action_and_board_values(self):
        """str(node) mentions the action taken and the board's tile values."""
        node = Node([[1, 2], [3, 0]], Action.UP)
        text = str(node)
        self.assertIn("up", text)
        self.assertIn("1", text)

    def test_str_reports_none_when_no_action(self):
        """str(node) reports "None" for the action on the root node."""
        node = Node([[1, 2], [3, 0]])
        self.assertIn("None", str(node))

    def test_print_history_logs_ancestors_before_self(self):
        """print_history() logs the root node before its descendants, at INFO level."""
        root = Node([[1, 2], [3, 0]])
        child = Node([[1, 2], [0, 3]], Action.LEFT, root, 1)

        with self.assertLogs("Node", level="INFO") as log_context:
            child.print_history()
        output = "\n".join(log_context.output)

        self.assertLess(output.index("None"), output.index("left"))


if __name__ == "__main__":
    unittest.main()
