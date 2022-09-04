# cdata (Python dataclass for C structure/ binary data)

Integration of python dataclass and ctypes structured data.

This library provides a simple API for encoding/decoding dataclasses into ctypes.Structure/ctypes.Union.

This library can be used for:

- handling binary data.
- bridging the C API and python application.

## Overview

### Simple structure

```python
import ctypes
from dataclasses import dataclass
from typing import List

from cdata import big, field, little


@little
@dataclass
class LittleEndianItem:
    number: int = field(ctypes.c_uint32)
    string: str = field(ctypes.c_char * 5)


# Can use as normal dataclass
lei = LittleEndianItem(9999, "ABCDE")
print(lei.number, lei.string)  # => 9999 ABCDE


# Convert into ctypes.Structure
leic = lei.to_ctype()
print(isinstance(leic, ctypes.Structure))  # => True
print(leic.number, leic.string)  # => 9999 b'ABCDE'


# Create instance from ctypes.Structure
print(LittleEndianItem.from_ctype(leic) == lei)  # => True


# Create instance from buffer (equal to ctypes.Structure.from_buffer)
number = ctypes.c_uint32(9999)
string = (ctypes.c_char * 10)(b"A", b"B", b"C", b"D", b"E")
made_from_buffer = LittleEndianItem.from_buffer(bytearray(number) + bytearray(string))
print(made_from_buffer.number, made_from_buffer.string)  # => 9999 ABCDE

writable_buffer = bytearray(leic)
print(LittleEndianItem.from_buffer(writable_buffer) == lei)  # => True


# Create instance from buffer with copy (equal to ctypes.Structure.from_buffer_copy)
readable_buffer = bytes(leic)
print(LittleEndianItem.from_buffer_copy(readable_buffer) == lei)  # => True
```

### Nested structure and array

```python
@big
@dataclass
class NestedItem:
    nested_number: int = field(ctypes.c_uint32, 0)
    nested_string: str = field(ctypes.c_char * 10, "")


@big
@dataclass
class BigEndianData:
    number: int = field(ctypes.c_uint64, 0)
    string: str = field(ctypes.c_char * 20, "")
    item: NestedItem = field(NestedItem.ctype(), [])
    item_array: List[NestedItem] = field(NestedItem.ctype() * 5, [])
    int_array: List[int] = field(ctypes.c_uint16 * 5, [])


bed = BigEndianData(
    1,
    "littleendian_data",
    NestedItem(9999, "item9999"),
    [NestedItem(i, f"nested{i}") for i in range(5)],
    [i for i in range(5)],
)

bedc = bed.to_ctype()

# Nested item
print(bedc.item.nested_number, bedc.item.nested_string)  # => 9999 b'item9999'


# Array
print(bedc.item_array[0].nested_number, bedc.item_array[0].nested_string)  # => 0 b'nested0''
print(bedc.int_array[0], bedc.int_array[1], bedc.int_array[2])  # => 0 1 2


# Can create instance from buffer as well
print(BigEndianData.from_buffer_copy(bytes(bedc)) == bed)  # => True
print(BigEndianData.from_buffer(bytearray(bedc)) == bed)  # => True

```

### Use MixIn class

You can use MixIn class for inheritance instead of using decorators e.g. @little, @big

This may help the IDE work on intellisense and autocomplete.

```python
import ctypes
from dataclasses import dataclass
from typing import List

from cdata import DataClassLittleEndianStructureMixIn, field

@dataclass
class Base(DataClassLittleEndianStructureMixIn):
    _cdata_pack = 2  # Specify the ctypes.Structure._pack_ attribute here. Use 0 by default.


@dataclass
class Item(Base):
    item_number: int = field(ctypes.c_uint8)
    item_string: str = field(ctypes.c_char * 10)


@dataclass
class Data(Base):
    number: int = field(ctypes.c_uint32)
    string: str = field(ctypes.c_char * 20)
    item: Item = field(Item.ctype())
    items: List[Item] = field(Item.ctype() * 5)
    int_array: List[int] = field(ctypes.c_uint16 * 6)
    byte_array: List[int] = field(ctypes.c_byte * 7)
```
