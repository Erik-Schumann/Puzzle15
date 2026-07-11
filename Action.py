"""The moves the blank tile can make."""

from enum import Enum


class Action(Enum):
    """Move the blank tile can make on the puzzle board."""

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
