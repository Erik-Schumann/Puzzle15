"""Unit tests for NoSolutionError."""

import unittest

from NoSolutionError import NoSolutionError


class TestNoSolutionError(unittest.TestCase):
    """Tests for the NoSolutionError exception."""

    def test_is_an_exception_subclass(self):
        """NoSolutionError is a standard Exception, so it can be caught generically."""
        self.assertTrue(issubclass(NoSolutionError, Exception))

    def test_carries_its_message(self):
        """The message passed at raise time is preserved on the exception."""
        with self.assertRaises(NoSolutionError) as context:
            raise NoSolutionError("no solution exists")
        self.assertEqual(str(context.exception), "no solution exists")


if __name__ == "__main__":
    unittest.main()
