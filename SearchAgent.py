"""Search-space traversal: pop, goal-test, and expand nodes until a solution is found."""

import logging

from Fringe import Fringe
from ManhattanDistance import ManhattanDistance
from NoSolutionError import NoSolutionError

logger = logging.getLogger(__name__)


class SearchAgent:
    """Searches a Problem's state space, ordered by f(n) = a*g(n) + b*h(n)."""

    DEFAULT_LOG_INTERVAL = 50_000

    def __init__(
        self,
        heuristic=None,
        a=1.0,
        b=1.0,
        log_interval=None,
        track_visited=True,
        max_nodes_observed=None,
        max_fringe_size=None,
    ):
        """Pick a default heuristic and set up the fringe.

        `a`/`b` weight the evaluation function as f(n) = a*g(n) + b*h(n) — e.g.
        a=1,b=0 behaves like Dijkstra, a=0,b=1 like Greedy, a=1,b=1 like plain A*.
        `log_interval` controls how many loop iterations pass between DEBUG progress
        log messages. `track_visited` controls whether already-popped states are
        remembered and skipped (disabling it lets the same state be explored more
        than once). `max_nodes_observed`/`max_fringe_size` are optional upper limits;
        search() raises NoSolutionError with a descriptive message if either is
        exceeded before a goal is found. Logs the resulting configuration at DEBUG
        level.
        """
        self.heuristic = heuristic or ManhattanDistance() #by default use Manhattan Distance (e.g. Dijkstera Logging requires a heuristic, even though it does not influence the evaluation function f(n) )
        self.a = a
        self.b = b
        self.log_interval = log_interval or self.DEFAULT_LOG_INTERVAL
        self.track_visited = track_visited
        self.max_nodes_observed = max_nodes_observed
        self.max_fringe_size_limit = max_fringe_size
        self.fringe = Fringe(self.heuristic, a, b, track_visited=track_visited)
        self.nodes_observed = 0
        self.nodes_inserted = 0

        logger.debug(
            "SearchAgent created: heuristic=%s a=%s b=%s log_interval=%d track_visited=%s "
            "max_nodes_observed=%s max_fringe_size=%s",
            type(self.heuristic).__name__,
            self.a,
            self.b,
            self.log_interval,
            self.track_visited,
            self.max_nodes_observed,
            self.max_fringe_size_limit,
        )

    @property
    def max_fringe_size(self):
        """The largest number of nodes the fringe has held at any one time during search()."""
        return self.fringe.max_fringe_size

    def search(self, problem):
        """Run the search over `problem` and return the goal Node.

        Raises NoSolutionError if the fringe empties without finding one, or if
        `max_nodes_observed`/`max_fringe_size` is exceeded first (logged at WARNING
        level with which limit was hit, before raising).
        """
        # Step 1: seed the fringe with the initial node.
        self.fringe.push(problem.get_initial_node())

        while True:
            # Step 2: pop the next not-yet-visited node (raises NoSolutionError once exhausted).
            node = self.fringe.pop()
            self.nodes_observed += 1

            if self.max_nodes_observed is not None and self.nodes_observed > self.max_nodes_observed:
                message = (
                    f"Exceeded configured limit of {self.max_nodes_observed} observed nodes "
                    "without finding a solution."
                )
                logger.warning(message)
                raise NoSolutionError(message)

            # Log progress every log_interval loop iterations.
            if self.nodes_observed % self.log_interval == 0:
                logger.debug(
                    "%d nodes observed, %d inserted, lowest heuristic %s, evaluation %s, "
                    "max fringe size %d",
                    self.nodes_observed,
                    self.nodes_inserted,
                    self.fringe.lowest_heuristic,
                    self.fringe._evaluate(node),
                    self.fringe.max_fringe_size,
                )

            # Step 3: stop as soon as a goal state is popped.
            if problem.is_goal_state(node):
                logger.info(
                    "Goal state found: evaluation=%s heuristic=%s path_cost=%s max_fringe_size=%d",
                    self.fringe._evaluate(node),
                    self.heuristic.get_heuristic(node),
                    node.path_cost(),
                    self.fringe.max_fringe_size,
                )
                node.print_history()
                return node

            # Step 4: expand successors onto the fringe, counting only genuine insertions.
            for child in problem.get_successors(node):
                if self.fringe.push(child):
                    self.nodes_inserted += 1

                    if (
                        self.max_fringe_size_limit is not None
                        and self.fringe.max_fringe_size > self.max_fringe_size_limit
                    ):
                        message = (
                            f"Exceeded configured limit of {self.max_fringe_size_limit} "
                            "fringe size without finding a solution."
                        )
                        logger.warning(message)
                        raise NoSolutionError(message)
