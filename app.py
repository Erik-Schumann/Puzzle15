"""Entry point: solve a puzzle configuration with every algorithm/heuristic combination."""

import configparser
import logging
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402 (backend must be set before this import)

from HammingDistance import HammingDistance
from ManhattanDistance import ManhattanDistance
from NoSolutionError import NoSolutionError
from Problem import Problem
from SearchAgent import SearchAgent
from ZeroHeuristic import ZeroHeuristic

logger = logging.getLogger(__name__)

DEFAULT_CSV_PATH = "input/state_custom.csv"
DEFAULT_CONFIG_PATH = "input/config.ini"
DEFAULT_LOG_LEVEL = "WARNING"
DEFAULT_LOG_INTERVAL = SearchAgent.DEFAULT_LOG_INTERVAL
DEFAULT_CHART_PATH = "output/comparison.png"
DEFAULT_CONFIGURATIONS = [
    ("Greedy (Hamming)", "hamming", 0.0, 1.0, True),
    ("Greedy (Manhattan)", "manhattan", 0.0, 1.0, True),
    ("A* (Hamming)", "hamming", 1.0, 1.0, True),
    ("A* (Manhattan)", "manhattan", 1.0, 1.0, True),
]
HEURISTICS = {
    "hamming": HammingDistance,
    "manhattan": ManhattanDistance,
    "zero": ZeroHeuristic,
}

# Chart colors (validated categorical/chart-chrome palette; see DOCUMENTATION.md).
CHART_SURFACE = "#fcfcfb"
CHART_BAR = "#2a78d6"
CHART_INK_PRIMARY = "#0b0b0b"
CHART_INK_SECONDARY = "#52514e"
CHART_INK_MUTED = "#898781"
CHART_GRIDLINE = "#e1e0d9"
CHART_AXIS = "#c3c2b7"


def _read_config(path):
    """Parse an ini config file, treating trailing "# ..."/"; ..." text as a comment."""
    parser = configparser.ConfigParser(inline_comment_prefixes=("#", ";"))
    parser.read(path)
    return parser


def _preserve_case(optionstr: str) -> str:
    """Identity function used as a ConfigParser.optionxform override.

    ConfigParser lowercases option (key) names by default; search agents' labels
    are user-visible text, so their original case should be kept.
    """
    return optionstr


def resolve_log_level(path):
    """Read the [generalsettings] level from an ini config file, falling back to
    DEFAULT_LOG_LEVEL if the file/section/key is missing, or to WARNING if the level
    name isn't recognized.
    """
    parser = _read_config(path)
    level_name = parser.get("generalsettings", "level", fallback=DEFAULT_LOG_LEVEL).strip().upper()
    level = getattr(logging, level_name, None)
    return level if isinstance(level, int) else logging.WARNING


def resolve_log_interval(path):
    """Read the [generalsettings] log_interval from an ini config file: how many
    search-loop iterations pass between DEBUG progress log messages. Falls back to
    DEFAULT_LOG_INTERVAL if the file/section/key is missing or not a positive integer.
    """
    parser = _read_config(path)
    try:
        interval = parser.getint("generalsettings", "log_interval", fallback=DEFAULT_LOG_INTERVAL)
    except ValueError:
        return DEFAULT_LOG_INTERVAL
    return interval if interval > 0 else DEFAULT_LOG_INTERVAL


def resolve_max_nodes_observed(path):
    """Read the [generalsettings] max_nodes_observed from an ini config file: the upper
    limit on nodes SearchAgent.search() may observe before it raises NoSolutionError
    with a message naming this limit. Falls back to None (no limit) if the
    file/section/key is missing, blank, or not a positive integer.
    """
    parser = _read_config(path)
    try:
        value = parser.getint("generalsettings", "max_nodes_observed", fallback=None)
    except ValueError:
        return None
    return value if value and value > 0 else None


def resolve_max_fringe_size(path):
    """Read the [generalsettings] max_fringe_size from an ini config file: the upper
    limit on the fringe's peak size SearchAgent.search() may reach before it raises
    NoSolutionError with a message naming this limit. Falls back to None (no limit)
    if the file/section/key is missing, blank, or not a positive integer.
    """
    parser = _read_config(path)
    try:
        value = parser.getint("generalsettings", "max_fringe_size", fallback=None)
    except ValueError:
        return None
    return value if value and value > 0 else None


def resolve_csv_path(config_path):
    """Read the puzzle CSV path from the ini config file's [problem] state value,
    falling back to DEFAULT_CSV_PATH if it's missing or empty.
    """
    parser = _read_config(config_path)
    state = parser.get("problem", "state", fallback="").strip()
    return state or DEFAULT_CSV_PATH


def _parse_track_visited(value):
    """Coerce a track_visited field to bool: pass bools through, else look up the
    string in ConfigParser's own true/false spellings (case-insensitive). Raises
    KeyError for an unrecognized string, letting the caller treat it like any
    other malformed field.
    """
    if isinstance(value, bool):
        return value
    return configparser.ConfigParser.BOOLEAN_STATES[value.strip().lower()]


def resolve_configurations(config_path):
    """Read [searchagents] from an ini config file: one SearchAgent setup per line, as

        label = heuristic, a, b
        label = heuristic, a, b, track_visited

    where `heuristic` is hamming/manhattan/zero (blank to fall back to SearchAgent's
    own default), `a`/`b` weight f(n) = a*g(n) + b*h(n) — e.g. a=1,b=0 behaves like
    Dijkstra, a=0,b=1 like Greedy, a=1,b=1 like plain A* — and the optional
    `track_visited` (defaulting to true if omitted) controls whether that agent's
    Fringe remembers and skips already-popped states, per line. Returns a list of
    (label, Heuristic instance or None, a, b, track_visited) tuples, in file order.

    Falls back to DEFAULT_CONFIGURATIONS if the section is missing/empty. A line that
    doesn't parse (bad heuristic name, non-numeric a/b, unrecognized track_visited,
    or the wrong number of fields) is skipped with a warning printed to stdout,
    rather than raising.
    """
    parser = configparser.ConfigParser(inline_comment_prefixes=("#", ";"))
    parser.optionxform = _preserve_case  # keep each label's original case
    parser.read(config_path)

    if not parser.has_section("searchagents"):
        raw_entries = DEFAULT_CONFIGURATIONS
    else:
        raw_entries = [
            (label, *(part.strip() for part in value.split(",")))
            for label, value in parser.items("searchagents")
        ]
        if not raw_entries:
            raw_entries = DEFAULT_CONFIGURATIONS

    configurations = []
    for label, *fields in raw_entries:
        if len(fields) == 3:
            heuristic_name, a, b = fields
            track_visited_raw = True
        elif len(fields) == 4:
            heuristic_name, a, b, track_visited_raw = fields
        else:
            logger.warning("Skipping invalid configuration '%s': expected 3 or 4 fields, got %d", label, len(fields))
            continue

        try:
            heuristic = HEURISTICS[heuristic_name.lower()]() if heuristic_name else None
            weight_a = float(a)
            weight_b = float(b)
            track_visited = _parse_track_visited(track_visited_raw)
        except (ValueError, KeyError):
            logger.warning(
                "Skipping invalid configuration '%s': %s,%s,%s,%s", label, heuristic_name, a, b, track_visited_raw
            )
            continue
        configurations.append((label, heuristic, weight_a, weight_b, track_visited))

    return configurations or DEFAULT_CONFIGURATIONS


def plot_comparison(results, output_path=DEFAULT_CHART_PATH, problem_name=None):
    """Render a small-multiples bar-chart comparison of every solved configuration.

    `results` is a list of (label, path_cost, elapsed_ms, nodes_observed,
    nodes_inserted, max_fringe_size) tuples, one per configuration that found a
    solution. Each metric gets its own horizontal-bar subplot rather than sharing
    one axis, since moves/time/node-counts live on wildly different scales. Saves
    to `output_path` and returns it, or returns None (writing nothing) if
    `results` is empty. `problem_name`, if given, is appended to the chart header.
    """
    if not results:
        return None

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    labels = [row[0] for row in results]
    metrics = [
        ("Moves", [row[1] for row in results], "{:,.0f}"),
        ("Time (ms)", [row[2] for row in results], "{:,.1f}"),
        ("Nodes observed", [row[3] for row in results], "{:,.0f}"),
        ("Nodes inserted", [row[4] for row in results], "{:,.0f}"),
        ("Max fringe size", [row[5] for row in results], "{:,.0f}"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(16, max(4.0, 0.5 * len(labels)) * 2))
    fig.patch.set_facecolor(CHART_SURFACE)
    for unused_ax in axes.flat[len(metrics):]:
        unused_ax.axis("off")
    y_positions = range(len(labels))

    for ax, (title, values, value_format) in zip(axes.flat, metrics):
        ax.set_facecolor(CHART_SURFACE)
        bars = ax.barh(y_positions, values, height=0.6, color=CHART_BAR, zorder=3)

        ax.set_yticks(list(y_positions))
        ax.set_yticklabels(labels, color=CHART_INK_SECONDARY, fontsize=9)
        ax.invert_yaxis()  # first configuration on top
        ax.tick_params(axis="y", length=0)
        ax.tick_params(axis="x", colors=CHART_INK_MUTED, labelsize=8)

        ax.set_title(title, color=CHART_INK_PRIMARY, fontsize=11, loc="left", pad=8)
        for spine_name, spine in ax.spines.items():
            spine.set_visible(spine_name == "bottom")
            if spine_name == "bottom":
                spine.set_color(CHART_AXIS)

        ax.set_axisbelow(True)
        ax.grid(axis="x", color=CHART_GRIDLINE, linewidth=1, zorder=0)

        max_value = max(values, default=0)
        ax.set_xlim(0, max_value * 1.18 if max_value > 0 else 1)
        for bar, value in zip(bars, values):
            ax.text(
                bar.get_width() + max_value * 0.02,
                bar.get_y() + bar.get_height() / 2,
                value_format.format(value),
                va="center",
                ha="left",
                color=CHART_INK_SECONDARY,
                fontsize=8,
            )

    title = "SearchAgent configuration comparison"
    if problem_name:
        title += f" — {problem_name}"
    fig.suptitle(title, color=CHART_INK_PRIMARY, fontsize=13, x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(output_path, dpi=150, facecolor=CHART_SURFACE)
    plt.close(fig)
    return output_path


if __name__ == "__main__":
    #1. Input gather input and configure application
    logging.basicConfig(
        level=resolve_log_level(DEFAULT_CONFIG_PATH),
        format="%(levelname)s:%(name)s:%(message)s",
    )
    log_interval = resolve_log_interval(DEFAULT_CONFIG_PATH)
    max_nodes_observed = resolve_max_nodes_observed(DEFAULT_CONFIG_PATH)
    max_fringe_size = resolve_max_fringe_size(DEFAULT_CONFIG_PATH)
    configurations = resolve_configurations(DEFAULT_CONFIG_PATH)

    csv_path = resolve_csv_path(DEFAULT_CONFIG_PATH)
    # construct problem
    try:
        problem = Problem.from_csv(csv_path)
    except FileNotFoundError:
        logger.error("Could not find puzzle configuration file '%s'.", csv_path)
        sys.exit(1)
    except ValueError as error:
        logger.error("Invalid puzzle configuration in '%s': %s", csv_path, error)
        sys.exit(1)
    #2. Process Run each search agent and collect data for comparison chart
    results = []
    for label, heuristic, weight_a, weight_b, track_visited in configurations:
        agent = SearchAgent(
            heuristic,
            weight_a,
            weight_b,
            log_interval,
            track_visited=track_visited,
            max_nodes_observed=max_nodes_observed,
            max_fringe_size=max_fringe_size,
        )

        start_time = time.perf_counter()
        try:
            goal_node = agent.search(problem)
        except NoSolutionError as error:
            logger.info("%s: %s", label, error)
            continue
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "%s: solved in %d moves | time %.2f ms | observed %d | inserted %d | max fringe size %d",
            label,
            goal_node.path_cost(),
            elapsed_ms,
            agent.nodes_observed,
            agent.nodes_inserted,
            agent.max_fringe_size,
        )
        results.append(
            (
                label,
                goal_node.path_cost(),
                elapsed_ms,
                agent.nodes_observed,
                agent.nodes_inserted,
                agent.max_fringe_size,
            )
        )
    #3. Output Generate comparison chart
    chart_path = plot_comparison(results, problem_name=os.path.basename(csv_path))
    if chart_path:
        logger.info("Comparison chart written to %s", chart_path)
