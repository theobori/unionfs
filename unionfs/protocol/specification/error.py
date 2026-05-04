from enum import IntEnum


class ErrorMessageValue(IntEnum):
    MISSING_FIELD = 0
    BINDING_ALREADY_EXISTS = 1
    BINDING_DOES_NOT_EXIST = 2
    INVALID_INSERT_TYPE = 3  # It should never happens
    MOUNTPOINT_ALREADY_EXISTS = 4
    MOUNTPOINT_DOES_NOT_EXIST = 5
    SERVER_ERROR = 6
    INVALID_OBJECT_TYPE = 7
