import ctypes
from dataclasses import dataclass
from typing import List

import pytest
from cdata import Endian, big, field


@big
@dataclass
class BigItem:
    item_number: int = field(ctypes.c_uint8)
    item_string: str = field(ctypes.c_char * 10)


@big
@dataclass
class BigData:
    number: int = field(ctypes.c_uint32)
    string: str = field(ctypes.c_char * 20)
    item: BigItem = field(BigItem.ctype())
    items: List[BigItem] = field(BigItem.ctype() * 5)
    int_array: List[int] = field(ctypes.c_uint16 * 6)
    byte_array: List[int] = field(ctypes.c_byte * 7)


@pytest.fixture
def big_data():
    return BigData(
        1,
        "Data",
        BigItem(0, "A"),
        [BigItem(i, f"{i}") for i in range(5)],
        [i for i in range(6)],
        [i for i in range(7)],
    )


def test_cdata_endian(big_data):
    assert big_data.cdata_endian == Endian.BIG
    assert big_data.item.cdata_endian == Endian.BIG


def test_cdata_pack(big_data):
    assert big_data.cdata_pack == 1
    assert big_data.item.cdata_pack == 1


def test_big_to_ctype(big_data):
    c = big_data.to_ctype()
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


def test_big_from_ctype(big_data):
    c = big_data.to_ctype()
    o = BigData.from_ctype(c)
    assert o == big_data


def test_big_from_buffer(big_data):
    b = bytearray(big_data.to_ctype())
    o = BigData.from_buffer(b)
    assert o == big_data


def test_big_from_buffer_copy(big_data):
    b = bytes(big_data.to_ctype())
    o = BigData.from_buffer_copy(b)
    assert o == big_data
