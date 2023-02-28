import ctypes
from dataclasses import dataclass, field
from typing import List

import pytest
from cdata import LittleEndianCDataMixIn, meta


# Size = 14
@dataclass
class Item(LittleEndianCDataMixIn):
    f_item_number: int = field(metadata=meta(ctypes.c_uint32))
    f_item_bytes: bytes = field(metadata=meta(ctypes.c_char * 10))


# Size = 120
@dataclass
class Data(LittleEndianCDataMixIn):
    f_number: int = field(metadata=meta(ctypes.c_uint32))
    f_bytes: bytes = field(metadata=meta(ctypes.c_char * 20))
    f_item: Item = field(metadata=meta(Item.ctype()))
    f_items: List[Item] = field(metadata=meta(Item.ctype() * 5))
    f_int_array: List[int] = field(metadata=meta(ctypes.c_uint16 * 6))


@pytest.fixture
def data():
    return Data(
        1,
        b"Data",
        Item(0, b"A"),
        [Item(i, bytes(str(i), "utf-8")) for i in range(5)],
        [i for i in range(6)],
    )


@pytest.fixture
def c_data(data):
    return data.to_ctype()
