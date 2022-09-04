from dataclasses import dataclass, is_dataclass
from typing import Type, overload

from .core import DataClassCtypesMixIn, T
from .endian import Endian


@overload
def cdata(cls: Type[T], pack: int = 1) -> Type[T]:
    ...


@overload
def native(cls: Type[T], pack: int = 1) -> Type[T]:
    ...


@overload
def little(cls: Type[T], pack: int = 1) -> Type[T]:
    ...


@overload
def big(cls: Type[T], pack: int = 1) -> Type[T]:
    ...


def cdata(cls=None, *, endian: Endian, pack: int):
    """Wrap the dataclass with DataClassCtypesMixIn."""

    def wrap(cls: Type):
        if not is_dataclass(cls):
            dataclass(cls)
        return _process_class(cls, endian, pack)

    if cls is None:
        return wrap
    return wrap(cls)


def native(cls=None, *, pack: int = 1):
    """Wrap the dataclass with DataClassNativeEndianStructureMixIn."""
    return cdata(cls, endian=Endian.NATIVE, pack=pack)


def little(cls=None, *, pack: int = 1):
    """Wrap the dataclass with DataClassLittleEndianStructureMixIn."""
    return cdata(cls, endian=Endian.LITTLE, pack=pack)


def big(cls=None, *, pack: int = 1):
    """Wrap the dataclass with DataClassBigEndianStructureMixIn."""
    return cdata(cls, endian=Endian.BIG, pack=pack)


def union(cls=None, *, pack: int = 1):
    """Wrap the dataclass with DataClassNativeEndianStructureMixIn."""
    return cdata(cls, endian=Endian.NATIVE, pack=pack)


def _process_class(cls: Type, endian: Endian, pack: int):
    cls._cdata_endian = endian
    cls._cdata_pack = pack

    cls.cdata_endian = DataClassCtypesMixIn.cdata_endian
    cls.cdata_pack = DataClassCtypesMixIn.cdata_pack

    cls.ctype = classmethod(DataClassCtypesMixIn.ctype.__func__)
    cls.from_buffer = classmethod(DataClassCtypesMixIn.from_buffer.__func__)
    cls.from_buffer_copy = classmethod(DataClassCtypesMixIn.from_buffer_copy.__func__)
    cls.from_ctype = classmethod(DataClassCtypesMixIn.from_ctype.__func__)
    cls.to_ctype = DataClassCtypesMixIn.to_ctype
    cls.from_dict = classmethod(DataClassCtypesMixIn.from_dict.__func__)
    cls.to_dict = DataClassCtypesMixIn.to_dict

    DataClassCtypesMixIn.register(cls)

    return cls
