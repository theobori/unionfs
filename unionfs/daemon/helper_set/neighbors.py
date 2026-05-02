"""The helper set neighbors module."""

from dataclasses import dataclass


@dataclass
class Neighbors[T]:
    """Represents the previous and next neighbors."""

    previous: T
    next: T
