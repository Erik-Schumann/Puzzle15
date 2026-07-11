"""User-defined exception for an unsolvable puzzle."""


class NoSolutionError(Exception):
    """Raised by SearchAgent.search when the fringe empties without reaching the goal,
    or when a configured max_nodes_observed/max_fringe_size limit is exceeded first."""
