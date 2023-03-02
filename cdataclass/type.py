import ctypes
from typing import Any, Callable, Type, Union

SimpleCTypeClass = Union[
    Type[ctypes.c_bool],
    Type[ctypes.c_char],
    Type[ctypes.c_wchar],
    Type[ctypes.c_byte],
    Type[ctypes.c_ubyte],
    Type[ctypes.c_short],
    Type[ctypes.c_ushort],
    Type[ctypes.c_int],
    Type[ctypes.c_int8],
    Type[ctypes.c_int16],
    Type[ctypes.c_int32],
    Type[ctypes.c_int64],
    Type[ctypes.c_uint],
    Type[ctypes.c_uint8],
    Type[ctypes.c_uint16],
    Type[ctypes.c_uint32],
    Type[ctypes.c_uint64],
    Type[ctypes.c_long],
    Type[ctypes.c_ulong],
    Type[ctypes.c_longlong],
    Type[ctypes.c_ulonglong],
    Type[ctypes.c_size_t],
    Type[ctypes.c_ssize_t],
    Type[ctypes.c_float],
    Type[ctypes.c_double],
    Type[ctypes.c_longdouble],
    Type[ctypes.c_char_p],
    Type[ctypes.c_wchar_p],
    Type[ctypes.c_void_p],
]

SimpleCType = Union[
    ctypes.c_bool,
    ctypes.c_char,
    ctypes.c_wchar,
    ctypes.c_byte,
    ctypes.c_ubyte,
    ctypes.c_short,
    ctypes.c_ushort,
    ctypes.c_int,
    ctypes.c_int8,
    ctypes.c_int16,
    ctypes.c_int32,
    ctypes.c_int64,
    ctypes.c_uint,
    ctypes.c_uint8,
    ctypes.c_uint16,
    ctypes.c_uint32,
    ctypes.c_uint64,
    ctypes.c_long,
    ctypes.c_ulong,
    ctypes.c_longlong,
    ctypes.c_ulonglong,
    ctypes.c_size_t,
    ctypes.c_ssize_t,
    ctypes.c_float,
    ctypes.c_double,
    ctypes.c_longdouble,
    ctypes.c_char_p,
    ctypes.c_wchar_p,
    ctypes.c_void_p,
]

CTypeClass = Union[
    SimpleCTypeClass,
    Type[ctypes.Structure],
    Type[ctypes.Union],
    Type[ctypes.Array],
]

CType = Union[
    SimpleCType,
    ctypes.Structure,
    ctypes.Union,
    ctypes.Array,
]

StructuredCTypeClass = Union[Type[ctypes.Structure], Type[ctypes.Union]]
StructuredCType = Union[ctypes.Structure, ctypes.Union]

CTypeDecoder = Callable[[Any], Any]
CTypeEncoder = Callable[[Any], Any]
