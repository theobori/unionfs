"""The helper set module."""

from typing import Dict, Hashable, Iterable, Iterator, NoReturn, Optional

from unionfs.daemon.helper_set.exceptions import (
    HelperSetEmptyError,
    HelperSetValueNotExistError,
)
from unionfs.daemon.helper_set.neighbors import Neighbors
from unionfs.daemon.helper_set.node import Node


class HelperSet[T: Hashable]:
    """This is an implementation of a specific ordered set. It is only requires by
    the UnionFS daemon.

    It must be able to do the following operations:
    - LIFO value insertion a with time complexity describe by O(1)
    - FIFO value insertion a with time complexity describe by O(1)
    - LIFO value deletion a with time complexity describe by O(1)
    - FIFO value deletion a with time complexity describe by O(1)
    - Retrieving an inserted value a with time complexity describe by O(1)
    - Removing any value an inserted value a with time complexity describe by O(1)
    - Insert a value after another an inserted value a with time complexity describe by O(1)
    """

    def __init__(self, iterable: Optional[Iterable] = None):
        self._hashmap: Dict[T, Node[T][T]] = dict()
        self._head: Optional[Node] = None
        self._tail: Optional[Node] = None

        if iterable:
            for el in iterable:
                self.push(el)

    def push(self, value: T) -> NoReturn:
        """Add a value to the right.

        Args:
            value (T): The value.

        Returns:
            NoReturn: It returns nothing.
        """

        if value in self._hashmap:
            return

        node = Node(value=value, neighbors=Neighbors(previous=self._tail, next=None))
        if self._tail:
            self._tail.neighbors.next = node

        self._tail = node
        if self._head is None:
            self._head = node

        self._hashmap[value] = node

    def pushleft(self, value: T) -> NoReturn:
        """Add a value to the left.

        Args:
            value (T): The value.

        Returns:
            NoReturn: It returns nothing.
        """

        if value in self._hashmap:
            return

        node = Node(value=value, neighbors=Neighbors(previous=None, next=self._head))
        if self._head:
            self._head.neighbors.previous = node

        self._head = node
        if self._tail is None:
            self._tail = node

        self._hashmap[value] = node

    def pop(self) -> T:
        """Remove then returns the rightmost value.

        Raises:
            HelperSetEmptyError: If the set is empty.

        Returns:
            T: The rightmost value.
        """

        if self._tail is None:
            raise HelperSetEmptyError("The set is empty")

        tail = self._tail
        self._tail = self._tail.neighbors.previous

        if self._tail:
            self._tail.neighbors.next = None
        else:
            self._head = None

        del self._hashmap[tail.value]

        return tail.value

    def popleft(self) -> T:
        """Remove then returns the leftmost value.

        Raises:
            HelperSetEmptyError: If the set is empty.

        Returns:
            T: The leftmost value.
        """

        if self._head is None:
            raise HelperSetEmptyError("The set is empty")

        head = self._head
        self._head = self._head.neighbors.next

        if self._head:
            self._head.neighbors.previous = None
        else:
            self._tail = None

        del self._hashmap[head.value]

        return head.value

    def __iter__(self) -> Iterator:
        curr = self._head

        while curr:
            yield curr.value
            curr = curr.neighbors.next

    def __contains__(self, value: T) -> bool:
        return value in self._hashmap

    def remove(self, value: T) -> NoReturn:
        """Remove a specific value.

        Raises:
            HelperSetValueNotExistError: If the value does not exist

        Returns:
            NoReturn: It returns nothing.
        """

        if not value in self:
            raise HelperSetValueNotExistError(f"The value {value} does not exist")

        node = self._hashmap[value]
        previous = node.neighbors.previous
        _next = node.neighbors.next

        if previous:
            previous.neighbors.next = _next
        if _next:
            _next.neighbors.previous = previous
        if self._head is node:
            self._head = _next

        del self._hashmap[value]

    def push_after(self, value: T, after: T) -> NoReturn:
        """Push a value after a specific value.

        Raises:
            HelperSetValueNotExistError: If the value `after` does not exist

        Returns:
            NoReturn: It returns nothing.
        """

        if after not in self._hashmap:
            raise HelperSetValueNotExistError(f"The value {after} does not exist")
        if value in self._hashmap:
            return

        # should never be None by definition
        after_node = self._hashmap[after]
        after_node_next = after_node.neighbors.next

        node = Node(
            value=value, neighbors=Neighbors(previous=after_node, next=after_node_next)
        )

        if after_node_next:
            after_node_next.neighbors.previous = node

        after_node.neighbors.next = node

        self._hashmap[value] = node
