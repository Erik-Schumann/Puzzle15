"""Unit tests for app's config-file resolution helpers."""

import logging
import os
import tempfile
import unittest

import app
from ManhattanDistance import ManhattanDistance


class TestResolveLogLevel(unittest.TestCase):
    """Tests for reading the logging level out of an ini config file."""

    def _write_config(self, text):
        """Write `text` to a temporary ini file and return its path, cleaned up after the test."""
        config_file = tempfile.NamedTemporaryFile("w", suffix=".ini", delete=False)
        config_file.write(text)
        config_file.close()
        self.addCleanup(os.remove, config_file.name)
        return config_file.name

    def test_reads_a_valid_level_from_the_config_file(self):
        """A well-formed [generalsettings] level entry resolves to the matching logging constant."""
        path = self._write_config("[generalsettings]\nlevel = DEBUG\n")
        self.assertEqual(app.resolve_log_level(path), logging.DEBUG)

    def test_is_case_insensitive(self):
        """Lowercase level names resolve just like uppercase ones."""
        path = self._write_config("[generalsettings]\nlevel = info\n")
        self.assertEqual(app.resolve_log_level(path), logging.INFO)

    def test_falls_back_to_default_when_file_is_missing(self):
        """A nonexistent config path falls back to DEFAULT_LOG_LEVEL instead of raising."""
        level = app.resolve_log_level("does_not_exist_puzzle15.ini")
        self.assertEqual(level, getattr(logging, app.DEFAULT_LOG_LEVEL))

    def test_falls_back_to_default_when_section_is_missing(self):
        """A config file without a [generalsettings] section falls back to DEFAULT_LOG_LEVEL."""
        path = self._write_config("[other]\nkey = value\n")
        level = app.resolve_log_level(path)
        self.assertEqual(level, getattr(logging, app.DEFAULT_LOG_LEVEL))

    def test_falls_back_to_warning_for_an_unknown_level_name(self):
        """An unrecognized level name falls back to WARNING rather than raising."""
        path = self._write_config("[generalsettings]\nlevel = not_a_real_level\n")
        self.assertEqual(app.resolve_log_level(path), logging.WARNING)

    def test_strips_trailing_inline_comments(self):
        """A trailing "# ..." comment after the value doesn't become part of it."""
        path = self._write_config("[generalsettings]\nlevel = DEBUG # level of logging in the console\n")
        self.assertEqual(app.resolve_log_level(path), logging.DEBUG)


class TestResolveLogInterval(unittest.TestCase):
    """Tests for reading the SearchAgent log_interval out of an ini config file."""

    def _write_config(self, text):
        """Write `text` to a temporary ini file and return its path, cleaned up after the test."""
        config_file = tempfile.NamedTemporaryFile("w", suffix=".ini", delete=False)
        config_file.write(text)
        config_file.close()
        self.addCleanup(os.remove, config_file.name)
        return config_file.name

    def test_reads_a_valid_interval_from_the_config_file(self):
        """A well-formed [generalsettings] log_interval entry resolves to that integer."""
        path = self._write_config("[generalsettings]\nlog_interval = 100\n")
        self.assertEqual(app.resolve_log_interval(path), 100)

    def test_falls_back_to_default_when_file_is_missing(self):
        """A nonexistent config path falls back to DEFAULT_LOG_INTERVAL instead of raising."""
        interval = app.resolve_log_interval("does_not_exist_puzzle15.ini")
        self.assertEqual(interval, app.DEFAULT_LOG_INTERVAL)

    def test_falls_back_to_default_when_section_is_missing(self):
        """A config file without a [generalsettings] section falls back to DEFAULT_LOG_INTERVAL."""
        path = self._write_config("[other]\nkey = value\n")
        self.assertEqual(app.resolve_log_interval(path), app.DEFAULT_LOG_INTERVAL)

    def test_falls_back_to_default_for_a_non_integer_value(self):
        """A non-integer value falls back to DEFAULT_LOG_INTERVAL rather than raising."""
        path = self._write_config("[generalsettings]\nlog_interval = not_a_number\n")
        self.assertEqual(app.resolve_log_interval(path), app.DEFAULT_LOG_INTERVAL)

    def test_falls_back_to_default_for_a_non_positive_value(self):
        """A zero or negative interval falls back to DEFAULT_LOG_INTERVAL (0 would make
        SearchAgent's `nodes_observed % log_interval` check raise ZeroDivisionError)."""
        path = self._write_config("[generalsettings]\nlog_interval = 0\n")
        self.assertEqual(app.resolve_log_interval(path), app.DEFAULT_LOG_INTERVAL)


class TestResolveCsvPath(unittest.TestCase):
    """Tests for choosing which puzzle CSV to load."""

    def _write_config(self, text):
        """Write `text` to a temporary ini file and return its path, cleaned up after the test."""
        config_file = tempfile.NamedTemporaryFile("w", suffix=".ini", delete=False)
        config_file.write(text)
        config_file.close()
        self.addCleanup(os.remove, config_file.name)
        return config_file.name

    def test_state_is_used_as_the_csv_path(self):
        """[problem] state is read back verbatim as the CSV path to load."""
        path = self._write_config("[problem]\nstate = input/state_30.csv\n")
        self.assertEqual(app.resolve_csv_path(path), "input/state_30.csv")

    def test_falls_back_to_default_when_file_is_missing(self):
        """A nonexistent config path falls back to DEFAULT_CSV_PATH instead of raising."""
        csv_path = app.resolve_csv_path("does_not_exist_puzzle15.ini")
        self.assertEqual(csv_path, app.DEFAULT_CSV_PATH)

    def test_falls_back_to_default_when_section_is_missing(self):
        """A config file without a [problem] section falls back to DEFAULT_CSV_PATH."""
        path = self._write_config("[other]\nkey = value\n")
        self.assertEqual(app.resolve_csv_path(path), app.DEFAULT_CSV_PATH)

    def test_falls_back_to_default_when_state_is_empty(self):
        """An empty/unset [problem] state value falls back to DEFAULT_CSV_PATH."""
        path = self._write_config("[problem]\nstate =\n")
        self.assertEqual(app.resolve_csv_path(path), app.DEFAULT_CSV_PATH)


class TestResolveConfigurations(unittest.TestCase):
    """Tests for reading the per-line SearchAgent configurations out of an ini config file."""

    def _write_config(self, text):
        """Write `text` to a temporary ini file and return its path, cleaned up after the test."""
        config_file = tempfile.NamedTemporaryFile("w", suffix=".ini", delete=False)
        config_file.write(text)
        config_file.close()
        self.addCleanup(os.remove, config_file.name)
        return config_file.name

    def test_reads_a_well_formed_configuration_line(self):
        """A well-formed 3-field line resolves to (label, heuristic instance, a, b, True)."""
        path = self._write_config("[searchagents]\nMy Astar = manhattan, 1, 5\n")
        configurations = app.resolve_configurations(path)

        self.assertEqual(len(configurations), 1)
        label, heuristic, a, b, track_visited = configurations[0]
        self.assertEqual(label, "My Astar")
        self.assertIsInstance(heuristic, ManhattanDistance)
        self.assertEqual(a, 1.0)
        self.assertEqual(b, 5.0)
        self.assertTrue(track_visited)

    def test_preserves_the_label_case_and_file_order(self):
        """Labels keep their original case, and entries come back in file order."""
        path = self._write_config(
            "[searchagents]\n"
            "Zebra = hamming, 0, 1\n"
            "Apple = manhattan, 1, 1\n"
        )
        labels = [entry[0] for entry in app.resolve_configurations(path)]
        self.assertEqual(labels, ["Zebra", "Apple"])

    def test_blank_heuristic_means_no_heuristic(self):
        """A blank heuristic field (for a Dijkstra-equivalent b=0) resolves to a None heuristic."""
        path = self._write_config("[searchagents]\nDijkstra = , 1, 0\n")
        _, heuristic, a, b, _ = app.resolve_configurations(path)[0]
        self.assertIsNone(heuristic)
        self.assertEqual(a, 1.0)
        self.assertEqual(b, 0.0)

    def test_falls_back_to_default_when_file_is_missing(self):
        """A nonexistent config path resolves the same labels as DEFAULT_CONFIGURATIONS."""
        configurations = app.resolve_configurations("does_not_exist_puzzle15.ini")
        labels = [entry[0] for entry in configurations]
        default_labels = [entry[0] for entry in app.DEFAULT_CONFIGURATIONS]
        self.assertEqual(labels, default_labels)

    def test_falls_back_to_default_when_section_is_missing(self):
        """A config file without a [searchagents] section resolves DEFAULT_CONFIGURATIONS."""
        path = self._write_config("[other]\nkey = value\n")
        configurations = app.resolve_configurations(path)
        labels = [entry[0] for entry in configurations]
        default_labels = [entry[0] for entry in app.DEFAULT_CONFIGURATIONS]
        self.assertEqual(labels, default_labels)

    def test_skips_a_line_with_an_unknown_heuristic(self):
        """A line naming an unrecognized heuristic is skipped rather than raising."""
        path = self._write_config(
            "[searchagents]\n"
            "Bad = not_a_heuristic, 1, 1\n"
            "Good = hamming, 0, 1\n"
        )
        configurations = app.resolve_configurations(path)
        labels = [entry[0] for entry in configurations]
        self.assertEqual(labels, ["Good"])

    def test_falls_back_to_default_when_every_line_is_invalid(self):
        """If every line fails to parse, falls back to DEFAULT_CONFIGURATIONS rather
        than silently running zero configurations."""
        path = self._write_config("[searchagents]\nBad = not_a_heuristic, 1, 1\n")
        self.assertEqual(app.resolve_configurations(path), app.DEFAULT_CONFIGURATIONS)

    def test_skips_a_line_with_non_numeric_weights(self):
        """A line with a non-numeric a/b is skipped rather than raising."""
        path = self._write_config(
            "[searchagents]\n"
            "Bad = hamming, x, 1\n"
            "Good = hamming, 0, 1\n"
        )
        labels = [entry[0] for entry in app.resolve_configurations(path)]
        self.assertEqual(labels, ["Good"])

    def test_defaults_track_visited_to_true_when_field_is_omitted(self):
        """A 3-field line (no track_visited) defaults that agent to track_visited=True."""
        path = self._write_config("[searchagents]\nGood = hamming, 0, 1\n")
        _, _, _, _, track_visited = app.resolve_configurations(path)[0]
        self.assertTrue(track_visited)

    def test_reads_an_explicit_true_track_visited_field(self):
        """A 4th field of 'true' resolves that agent's track_visited to True."""
        path = self._write_config("[searchagents]\nGood = hamming, 0, 1, true\n")
        _, _, _, _, track_visited = app.resolve_configurations(path)[0]
        self.assertTrue(track_visited)

    def test_reads_an_explicit_false_track_visited_field(self):
        """A 4th field of 'false' resolves that agent's track_visited to False."""
        path = self._write_config("[searchagents]\nGood = hamming, 0, 1, false\n")
        _, _, _, _, track_visited = app.resolve_configurations(path)[0]
        self.assertFalse(track_visited)

    def test_track_visited_is_independent_per_line(self):
        """Different lines can mix track_visited=true and track_visited=false."""
        path = self._write_config(
            "[searchagents]\n"
            "Tracked = hamming, 0, 1, true\n"
            "Untracked = hamming, 0, 1, false\n"
        )
        configurations = app.resolve_configurations(path)
        track_visited_by_label = {label: track_visited for label, _, _, _, track_visited in configurations}
        self.assertTrue(track_visited_by_label["Tracked"])
        self.assertFalse(track_visited_by_label["Untracked"])

    def test_skips_a_line_with_an_unrecognized_track_visited_value(self):
        """A 4th field that isn't a recognized boolean is skipped rather than raising."""
        path = self._write_config(
            "[searchagents]\n"
            "Bad = hamming, 0, 1, not_a_bool\n"
            "Good = hamming, 0, 1\n"
        )
        labels = [entry[0] for entry in app.resolve_configurations(path)]
        self.assertEqual(labels, ["Good"])

    def test_skips_a_line_with_the_wrong_number_of_fields(self):
        """A line with fewer than 3 or more than 4 fields is skipped rather than raising."""
        path = self._write_config(
            "[searchagents]\n"
            "Bad = hamming, 0\n"
            "Good = hamming, 0, 1\n"
        )
        labels = [entry[0] for entry in app.resolve_configurations(path)]
        self.assertEqual(labels, ["Good"])


class TestResolveMaxNodesObserved(unittest.TestCase):
    """Tests for reading the [generalsettings] max_nodes_observed limit out of an ini config file."""

    def _write_config(self, text):
        """Write `text` to a temporary ini file and return its path, cleaned up after the test."""
        config_file = tempfile.NamedTemporaryFile("w", suffix=".ini", delete=False)
        config_file.write(text)
        config_file.close()
        self.addCleanup(os.remove, config_file.name)
        return config_file.name

    def test_reads_a_valid_limit_from_the_config_file(self):
        """A well-formed max_nodes_observed entry resolves to that integer."""
        path = self._write_config("[generalsettings]\nmax_nodes_observed = 1000\n")
        self.assertEqual(app.resolve_max_nodes_observed(path), 1000)

    def test_falls_back_to_none_when_file_is_missing(self):
        """A nonexistent config path falls back to None (no limit) instead of raising."""
        self.assertIsNone(app.resolve_max_nodes_observed("does_not_exist_puzzle15.ini"))

    def test_falls_back_to_none_when_key_is_blank(self):
        """A blank value falls back to None (no limit) rather than raising."""
        path = self._write_config("[generalsettings]\nmax_nodes_observed =\n")
        self.assertIsNone(app.resolve_max_nodes_observed(path))

    def test_falls_back_to_none_for_a_non_positive_value(self):
        """A zero or negative limit falls back to None (no limit) rather than raising."""
        path = self._write_config("[generalsettings]\nmax_nodes_observed = 0\n")
        self.assertIsNone(app.resolve_max_nodes_observed(path))

    def test_falls_back_to_none_for_a_non_integer_value(self):
        """A non-integer value falls back to None (no limit) rather than raising."""
        path = self._write_config("[generalsettings]\nmax_nodes_observed = not_a_number\n")
        self.assertIsNone(app.resolve_max_nodes_observed(path))


class TestResolveMaxFringeSize(unittest.TestCase):
    """Tests for reading the [generalsettings] max_fringe_size limit out of an ini config file."""

    def _write_config(self, text):
        """Write `text` to a temporary ini file and return its path, cleaned up after the test."""
        config_file = tempfile.NamedTemporaryFile("w", suffix=".ini", delete=False)
        config_file.write(text)
        config_file.close()
        self.addCleanup(os.remove, config_file.name)
        return config_file.name

    def test_reads_a_valid_limit_from_the_config_file(self):
        """A well-formed max_fringe_size entry resolves to that integer."""
        path = self._write_config("[generalsettings]\nmax_fringe_size = 500\n")
        self.assertEqual(app.resolve_max_fringe_size(path), 500)

    def test_falls_back_to_none_when_file_is_missing(self):
        """A nonexistent config path falls back to None (no limit) instead of raising."""
        self.assertIsNone(app.resolve_max_fringe_size("does_not_exist_puzzle15.ini"))

    def test_falls_back_to_none_when_key_is_blank(self):
        """A blank value falls back to None (no limit) rather than raising."""
        path = self._write_config("[generalsettings]\nmax_fringe_size =\n")
        self.assertIsNone(app.resolve_max_fringe_size(path))

    def test_falls_back_to_none_for_a_non_positive_value(self):
        """A zero or negative limit falls back to None (no limit) rather than raising."""
        path = self._write_config("[generalsettings]\nmax_fringe_size = 0\n")
        self.assertIsNone(app.resolve_max_fringe_size(path))

    def test_falls_back_to_none_for_a_non_integer_value(self):
        """A non-integer value falls back to None (no limit) rather than raising."""
        path = self._write_config("[generalsettings]\nmax_fringe_size = not_a_number\n")
        self.assertIsNone(app.resolve_max_fringe_size(path))


class TestPlotComparison(unittest.TestCase):
    """Tests for the small-multiples comparison chart."""

    def _output_path(self, name="comparison_test.png"):
        """Return a temp-directory path for a chart file, cleaned up after the test."""
        path = os.path.join(tempfile.gettempdir(), name)
        self.addCleanup(lambda: os.remove(path) if os.path.exists(path) else None)
        return path

    def test_returns_none_and_writes_nothing_for_empty_results(self):
        """With no solved configurations, there's nothing to chart."""
        path = self._output_path()
        self.assertIsNone(app.plot_comparison([], output_path=path))
        self.assertFalse(os.path.exists(path))

    def test_writes_a_chart_file_and_returns_its_path(self):
        """A non-empty results list is rendered to output_path and that path is returned."""
        path = self._output_path()
        results = [
            ("Greedy (Hamming)", 12, 1.5, 30, 60, 15),
            ("A* (Manhattan)", 12, 0.4, 13, 28, 9),
        ]
        returned_path = app.plot_comparison(results, output_path=path)
        self.assertEqual(returned_path, path)
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)

    def test_handles_a_single_result(self):
        """A single solved configuration still renders without error."""
        path = self._output_path()
        results = [("Only Config", 5, 2.0, 10, 20, 8)]
        app.plot_comparison(results, output_path=path)
        self.assertTrue(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
