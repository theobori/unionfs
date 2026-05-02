"""The helper set test module."""

import unittest

from unionfs.daemon.helper_set.helper_set import HelperSet
from unionfs.daemon.helper_set.exceptions import (
    HelperSetEmptyError,
    HelperSetValueNotExistError,
)


class TestHelperSet(unittest.TestCase):
    """Represents the helper set test cases."""

    def test_push(self):
        """Test the helper set push method"""

        hs = HelperSet()

        hs.push(1)
        hs.push(1)
        hs.push(2)
        hs.push(1)
        hs.push(3)
        hs.push(2)
        hs.push(4)
        hs.push(3)
        hs.push(4)

        self.assertListEqual(list(hs), [1, 2, 3, 4])

    def test_pushleft(self):
        """Test the helper set pushleft method"""

        hs = HelperSet()

        hs.pushleft(1)
        hs.pushleft(1)
        hs.pushleft(2)
        hs.pushleft(1)
        hs.pushleft(3)
        hs.pushleft(2)
        hs.pushleft(4)
        hs.pushleft(3)
        hs.pushleft(4)

        self.assertListEqual(list(hs), [4, 3, 2, 1])

    def test_pop(self):
        """Test the helper set pop method"""

        hs = HelperSet([1, 2, 3, 4])

        self.assertListEqual(list(hs), [1, 2, 3, 4])
        hs.pop()
        self.assertListEqual(list(hs), [1, 2, 3])
        hs.pop()
        self.assertListEqual(list(hs), [1, 2])
        hs.pop()
        self.assertListEqual(list(hs), [1])
        hs.pop()
        self.assertListEqual(list(hs), [])

        with self.assertRaises(HelperSetEmptyError):
            hs.pop()

    def test_remove(self):
        """Test the helper set remove method"""

        hs = HelperSet([1, 2, 3, 4])

        self.assertListEqual(list(hs), [1, 2, 3, 4])
        hs.popleft()
        self.assertListEqual(list(hs), [2, 3, 4])
        hs.popleft()
        self.assertListEqual(list(hs), [3, 4])
        hs.popleft()
        self.assertListEqual(list(hs), [4])
        hs.popleft()
        self.assertListEqual(list(hs), [])

        with self.assertRaises(HelperSetEmptyError):
            hs.popleft()

    def test_remove(self):
        """Test the helper set remove method"""

        hs = HelperSet([1, 2, 3, 4])

        self.assertListEqual(list(hs), [1, 2, 3, 4])
        hs.remove(2)
        self.assertListEqual(list(hs), [1, 3, 4])
        hs.remove(3)
        self.assertListEqual(list(hs), [1, 4])
        hs.remove(4)
        self.assertListEqual(list(hs), [1])
        hs.remove(1)
        self.assertListEqual(list(hs), [])

        with self.assertRaises(HelperSetValueNotExistError):
            hs.remove(0xDEADBEEF)

    def push_after(self):
        """Test the helper set push_after method"""

        hs = HelperSet([1, 2, 3, 4])

        self.assertListEqual(list(hs), [1, 2, 3, 4])
        hs.push_after(-1, 1)
        self.assertListEqual(list(hs), [1, -1, 3, 4])
        hs.push_after(-2, 2)
        self.assertListEqual(list(hs), [1, -1, 3, -3, 4])
        hs.push_after(-3, 3)
        self.assertListEqual(list(hs), [1, -1, 3, -3, 4, -4])

        with self.assertRaises(HelperSetValueNotExistError):
            hs.remove(0xDEADBEEF)
