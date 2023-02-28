import ctypes
from dataclasses import dataclass, field
from typing import List

import pytest
from cdata import LittleEndianCDataMixIn, meta


@dataclass
class Item(LittleEndianCDataMixIn):
    f_item_number: int = field(metadata=meta(ctypes.c_uint32))
    f_item_bytes: bytes = field(metadata=meta(ctypes.c_char * 10))


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


def test_to_ctype(data):
    c = data.to_ctype()
    assert c.f_number == 1
    assert c.f_bytes == b"Data"
    assert c.f_item.f_item_number == 0
    assert c.f_item.f_item_bytes == b"A"
    assert c.f_items[0].f_item_number == 0
    assert c.f_items[0].f_item_bytes == b"0"
    assert c.f_items[1].f_item_number == 1
    assert c.f_items[1].f_item_bytes == b"1"
    assert c.f_int_array[0] == 0
    assert c.f_int_array[5] == 5


def test_decode_and_encode():
    @dataclass
    class WithEncoderDecoder(LittleEndianCDataMixIn):
        f_string: str = field(
            metadata=meta(
                ctypes.c_char * 10,
                decoder=lambda v: v.decode("utf-8"),
                encoder=lambda v: v.encode("utf-8"),
            )
        )

    wed = WithEncoderDecoder("test")
    toc = wed.to_ctype()
    assert toc.f_string == b"test"
    fromc = WithEncoderDecoder.from_ctype(toc)
    assert fromc.f_string == "test"


def test_from_ctype(c_data, data):
    d = Data.from_ctype(c_data)
    assert d == data


def test_from_buffer(c_data, data):
    b = bytearray(c_data)
    d = Data.from_buffer(b)
    assert d == data

    number = ctypes.c_uint32(9999)
    string = (ctypes.c_char * 10)(
        b"A", b"B", b"C", b"D", b"E", b"F", b"G", b"H", b"I", b"J"
    )
    buffer = bytearray(number) + bytearray(string)
    i = Item.from_buffer(buffer)
    assert i.f_item_number == 9999
    assert i.f_item_bytes == b"ABCDEFGHIJ"


def test_from_buffer_copy(c_data, data):
    b = bytes(c_data)
    d = Data.from_buffer_copy(b)
    assert d == data
