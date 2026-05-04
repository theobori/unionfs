from enum import IntEnum


class ActionValue(IntEnum):
    BIND = 0
    SHOW = 1
    SHOW_ALL = 2
    MOUNT = 3
    UMOUNT = 4
    UNBIND = 5
