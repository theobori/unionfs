"""The common bind module."""

from enum import Enum


class InsertType(Enum):
    """Represents the different insert types available during binding."""

    AFTER = 0
    BEFORE = 1

    @staticmethod
    def from_str(s: str, ignore_case: bool = False) -> "InsertType":
        match s if ignore_case is False else s.lower():
            case "after":
                return InsertType.AFTER
            case "before":
                return InsertType.BEFORE
            case _:
                raise ValueError("Invalid value.")

    @staticmethod
    def from_value(value: int) -> "InsertType":
        m = InsertType._value2member_map_

        if not value in m:
            raise ValueError("Invalid value.")

        return InsertType._value2member_map_[value]
