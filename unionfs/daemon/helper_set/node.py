"""The helper set node module."""

from dataclasses import dataclass

from unionfs.daemon.helper_set.neighbors import Neighbors


@dataclass
class Node[V]:
    """Represents a node."""

    value: V
    neighbors: Neighbors["Node"]
