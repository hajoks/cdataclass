import ctypes
from dataclasses import dataclass

import pytest
from cdata import DataClassLittleEndianStructureMixIn, field, little


def test_field_with_default():
    @dataclass
    class Data(DataClassLittleEndianStructureMixIn):
        number: int = field(ctypes.c_uint16, 9999)
        string: str = field(ctypes.c_char * 10, "default")

    d = Data()
    assert d.number == 9999
    assert d.string == "default"


def test_field_without_default():
    @little
    @dataclass
    class Data:
        number: int = field(ctypes.c_uint16)
        string: str = field(ctypes.c_char * 10, "default")

    d = Data()
    assert d.number is None
    assert d.string == "default"


def test_field_default_with_too_many_length():
    with pytest.raises(ValueError) as e:

        class Data(DataClassLittleEndianStructureMixIn):
            number: int = field(ctypes.c_uint16, 9999)
            string: str = field(ctypes.c_char * 10, "defaultstring")

    assert str(e.value).endswith("field must be equall or less than 10")
