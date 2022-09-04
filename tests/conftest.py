import ctypes
from dataclasses import dataclass
from typing import List

import pytest
from cdata import DataClassBigEndianStructureMixIn, field


@dataclass
class MixInBase(DataClassBigEndianStructureMixIn):
    ...


@dataclass
class MixInItem(MixInBase):
    number: int = field(ctypes.c_uint8)
    string: str = field(ctypes.c_char * 10)


@dataclass
class MixInData(MixInBase):
    number: int = field(ctypes.c_uint32)
    string: str = field(ctypes.c_char * 20)
    item: MixInItem = field(MixInItem.ctype())
    items: List[MixInItem] = field(MixInItem.ctype() * 5)
    int_array: List[int] = field(ctypes.c_uint16 * 6)
    byte_array: List[int] = field(ctypes.c_byte * 7)


@pytest.fixture
def mixin_data():
    return MixInData(
        1,
        "Data",
        MixInItem(0, "A"),
        [MixInItem(i, f"{i}") for i in range(5)],
        [i for i in range(6)],
        [i for i in range(7)],
    )
