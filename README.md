# cdataclass - Python dataclass for C structure

## Overview

Integration of python dataclass and ctypes.Structure.

This library provides some API for encoding/decoding dataclasses into/from ctypes.Structure/ctypes.Union.

This library can be used for:

- handling packed binary data.
- bridging the C API and python application.

## Installation
```bash
$ pip install cdataclass
```

## Examples

```python

import ctypes
from dataclasses import dataclass, field
from typing import List

from cdataclass import BigEndianCDataMixIn, meta


# Simple big endian C structure
@dataclass
class Item(BigEndianCDataMixIn):
    f_item_number: int = field(metadata=meta(ctypes.c_uint32))
    f_item_bytes: bytes = field(metadata=meta(ctypes.c_char * 10))


# Use as normal dataclass
item = Item(1, b"test")
assert item.f_item_number == 1
assert item.f_item_bytes == b"test"


# Get corresponding ctypes.Structure class
c_item_class = Item.ctype()
assert issubclass(c_item_class, ctypes.BigEndianStructure)
assert hasattr(c_item_class, "_fields_")
assert hasattr(c_item_class, "_pack_")


# Get the size of corresponding ctypes.Structure class
assert Item.size() == 14  # uint32(4 bytes) + c_char * 10(10 bytes) = 14


# Convert to ctype.Structure instance
c_item = item.to_ctype()
assert isinstance(c_item, ctypes.BigEndianStructure)
assert c_item.f_item_number == 1
assert c_item.f_item_bytes == b"test"


# Serialize/Deserialize to/from buffer
hex_str_represents_uint32_100 = "00 00 00 64"
hex_str_represents_char_ABCDEFGHIJ = "41 42 43 44 45 46 47 48 49 4A"
buffer = bytearray.fromhex(hex_str_represents_uint32_100 + " " + hex_str_represents_char_ABCDEFGHIJ)
item = Item.from_buffer(buffer)
assert item.f_item_number == 100
assert item.f_item_bytes == b"ABCDEFGHIJ"
assert item.to_bytearray() == buffer


# Serialize/Deserialize to/from immutable buffer
immutable_buffer = bytes(buffer)
item = Item.from_buffer_copy(immutable_buffer)
assert item.f_item_number == 100
assert item.f_item_bytes == b"ABCDEFGHIJ"
assert item.to_bytes() == immutable_buffer


# Use custom ecoding/decoding functions for data conversion
@dataclass
class CustomItem(BigEndianCDataMixIn):
    f_number: int = field(
        metadata=meta(
            ctypes.c_char * 10,
            encoder=lambda v: str(v).rjust(10).encode("utf-8"),
            decoder=lambda v: int(v.decode("utf-8")),
        )
    )
    f_string: str = field(
        metadata=meta(
            ctypes.c_char * 10,
            encoder=lambda v: v.encode("utf-8"),
            decoder=lambda v: v.decode("utf-8"),
        )
    )


custom_item = CustomItem(100, "test")

# Encode as specified
c_custom_item = custom_item.to_ctype()
assert c_custom_item.f_number == b"       100"
assert c_custom_item.f_string == b"test"

# Decode as specified
custom_item = CustomItem.from_buffer_copy(custom_item.to_bytes())
assert custom_item.f_number == 100
assert custom_item.f_string == "test"


# Nested structure
@dataclass
class Data(BigEndianCDataMixIn):
    f_number: int = field(metadata=meta(ctypes.c_uint32))
    f_bytes: bytes = field(metadata=meta(ctypes.c_char * 20))
    # Use cls.ctype() to define a nested structure or array of structure or whatever customized
    f_item: Item = field(metadata=meta(Item.ctype()))
    f_items: List[Item] = field(metadata=meta(Item.ctype() * 5))
    f_int_array: List[int] = field(metadata=meta(ctypes.c_uint16 * 5))


data = Data(
    1,
    b"data",
    Item(100, b"item"),
    [Item(i, bytes(f"item{i}", "utf-8")) for i in range(5)],
    [i for i in range(5)],
)

# Access the nested field
c_data = data.to_ctype()
assert c_data.f_item.f_item_number == 100
assert c_data.f_item.f_item_bytes == b"item"

# Access the nested array
assert c_data.f_items[0].f_item_number == 0
assert c_data.f_items[0].f_item_bytes == b"item0"
assert c_data.f_items[4].f_item_number == 4
assert c_data.f_items[4].f_item_bytes == b"item4"

assert c_data.f_int_array[0] == 0
assert c_data.f_int_array[4] == 4

```
