from enum import Enum, auto


class Endian(str, Enum):
    NATIVE = auto()
    BIG = auto()
    LITTLE = auto()
    UNION = auto()
