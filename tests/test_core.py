import ctypes
import time
from dataclasses import dataclass
from typing import List

import pytest
from cdata import DataClassLittleEndianStructureMixIn, Endian, field


@dataclass
class MixInItem(DataClassLittleEndianStructureMixIn):
    item_number: int = field(ctypes.c_uint32)
    item_string: str = field(ctypes.c_char * 10)


@dataclass
class MixInData(DataClassLittleEndianStructureMixIn):
    number: int = field(ctypes.c_uint32)
    string: str = field(ctypes.c_char * 20)
    item: MixInItem = field(MixInItem.ctype())
    items: List[MixInItem] = field(MixInItem.ctype() * 5)
    int_array: List[int] = field(ctypes.c_uint16 * 6)
    byte_array: List[int] = field(ctypes.c_byte * 7)


@dataclass
class PureData:
    number: int
    string: str


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


def test_cdata_endian(mixin_data):
    assert mixin_data.cdata_endian == Endian.LITTLE


def test_cdata_pack(mixin_data):
    assert mixin_data.cdata_pack == 1


def test_to_ctype(mixin_data):
    s_not_cached = time.time()
    c = mixin_data.to_ctype()
    e_not_cached = time.time()
    assert c._pack_ == 1
    assert c.number == 1
    assert c.string == b"Data"
    assert c.item.item_number == 0
    assert c.item.item_string == b"A"
    assert c.items[0].item_number == 0
    assert c.items[0].item_string == b"0"
    assert c.items[1].item_number == 1
    assert c.items[1].item_string == b"1"
    assert c.int_array[0] == 0
    assert c.int_array[5] == 5
    assert c.byte_array[0] == 0
    assert c.byte_array[6] == 6

    s_cached = time.time()
    c = mixin_data.to_ctype()
    e_cached = time.time()

    assert e_cached - s_cached < e_not_cached - s_not_cached


def test_to_ctype_hook(mixin_data):
    def encode_hook(cname, ctype, cvalue, dataclass_value):
        if cname == "string":
            return b"hooked_value"
        return None

    c = mixin_data.to_ctype(hook=encode_hook)
    assert c.string == b"hooked_value"


def test_from_ctype(mixin_data):
    c = mixin_data.to_ctype()
    o = MixInData.from_ctype(c)
    assert o == mixin_data


def test_from_ctype_hook(mixin_data):
    c = mixin_data.to_ctype()

    def decode_hook(cname, ctype, cvalue):
        if cname == "string":
            return "hooked_value"
        return None

    o = MixInData.from_ctype(c, hook=decode_hook)
    assert o.string == "hooked_value"


def test_from_buffer(mixin_data):
    b = bytearray(mixin_data.to_ctype())
    o = MixInData.from_buffer(b)
    assert o == mixin_data

    number = ctypes.c_uint32(9999)
    string = (ctypes.c_char * 10)(b"A", b"B", b"C", b"D", b"E", b"F", b"G", b"H", b"I", b"J")
    buffer = bytearray(number) + bytearray(string)
    i = MixInItem.from_buffer(buffer)
    assert i.item_number == 9999
    assert i.item_string == "ABCDEFGHIJ"


def test_from_buffer_copy(mixin_data):
    b = bytes(mixin_data.to_ctype())
    o = MixInData.from_buffer_copy(b)
    assert o == mixin_data
