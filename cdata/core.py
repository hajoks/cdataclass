import abc
import ctypes
import types
from dataclasses import asdict, fields, make_dataclass
from typing import Any, Dict, Optional, Type, TypeVar, Union

from .cache import cache
from .endian import Endian
from .type import (CtypesDecoderHook, CtypesEncoderHook, CtypesStructuredData,
                   CtypesStructuredType, StructureName)

T = TypeVar("T", bound="DataClassCtypesMixIn")

_STRUCTURE_DATACLASS_MAP: Dict[StructureName, Type[T]] = {}


@cache(maxsize=1000)
def _create_ctype(datacls, base: CtypesStructuredType, pack: int) -> CtypesStructuredType:
    """
    Create a class of ctypes.Structure/ctypes.Union corresponding to the given dataclass.
    """
    structure_name = f"_generated_cypes_{datacls.__name__}"
    _ctypes_structure = types.new_class(name=structure_name, bases=(base,))
    _ctypes_structure._pack_ = pack
    _ctypes_structure._fields_ = [(f.name, f.metadata.get("ctype")) for f in fields(datacls)]

    # Cache the dataclass info for respective structure name which is dynamicaly defined
    _STRUCTURE_DATACLASS_MAP[structure_name] = datacls

    return _ctypes_structure


@cache(maxsize=1000)
def _create_dataclass(structure: CtypesStructuredType) -> Type[T]:
    """
    Create a dataclass corresponding to the given ctypes.Structure/ctypes.Union.
    Return cached class information if it's already defined in create_ctype.
    """
    # Get class info if there is an already defined dataclass for the coressponding structure
    cached = _STRUCTURE_DATACLASS_MAP.get(structure.__name__)
    if cached is not None:
        return cached

    _cdata_dataclass: Type[T] = make_dataclass(
        cls_name=f"_generated_cdata_{structure.__name__}",
        fields=[(fname, ftype) for fname, ftype in getattr(structure, "_fields_", [])],
        bases=(DataClassCtypesMixIn,),
    )
    if structure == ctypes.BigEndianStructure:
        _cdata_dataclass._cdata_endian = Endian.BIG
    elif structure == ctypes.LittleEndianStructure:
        _cdata_dataclass._cdata_endian = Endian.LITTLE
    else:
        _cdata_dataclass._cdata_endian = Endian.NATIVE
    _cdata_dataclass.cdata_pack = structure._pack_
    return _cdata_dataclass


def _ctype_to_dataclass(
    datacls: Type[T], structure: CtypesStructuredData, hook: Optional[CtypesDecoderHook] = None
) -> T:
    """Create a dataclass instance initialized with the given ctypes.Structure/ctype.Union"""
    d = {}
    for cname, ctype in getattr(structure, "_fields_", []):
        cvalue = getattr(structure, cname)
        if hook is not None and hook(cname, ctype, cvalue) is not None:
            d[cname] = hook(cname, ctype, cvalue)
            continue
        if isinstance(cvalue, int):
            d[cname] = cvalue
        if isinstance(cvalue, bytes):
            d[cname] = cvalue.decode()
        if hasattr(cvalue, "_length_") and hasattr(cvalue, "_type_"):
            if issubclass(cvalue._type_, ctypes.Structure) or issubclass(cvalue._type_, ctypes.Union):
                d[cname] = [_ctype_to_dataclass(_create_dataclass(cvalue._type_), e, hook) for e in cvalue]
            else:
                d[cname] = [e for e in cvalue]
        if hasattr(cvalue, "_fields_"):
            d[cname] = _ctype_to_dataclass(_create_dataclass(cvalue.__class__), cvalue, hook)
    return datacls(**d)


def _dataclass_to_ctype(datacls: T, hook: Optional[CtypesEncoderHook] = None) -> CtypesStructuredData:
    """Create a ctypes.Structure/ctype.Union instance from given dataclass instance."""
    structure = datacls.__class__.ctype()()
    for cname, ctype in getattr(structure, "_fields_", []):
        cvalue = getattr(structure, cname)
        dataclass_value = getattr(datacls, cname)
        if hook is not None and hook(cname, ctype, cvalue, dataclass_value) is not None:
            setattr(structure, cname, hook(cname, ctype, cvalue, dataclass_value))
            continue
        if isinstance(cvalue, int):
            setattr(structure, cname, dataclass_value)
        if isinstance(cvalue, bytes):
            setattr(structure, cname, bytes(dataclass_value, encoding="utf-8"))
        if hasattr(cvalue, "_length_") and hasattr(cvalue, "_type_"):
            if issubclass(cvalue._type_, ctypes.Structure) or issubclass(cvalue._type_, ctypes.Union):
                setattr(structure, cname, (ctype)(*[_dataclass_to_ctype(e, hook) for e in dataclass_value]))
            else:
                setattr(structure, cname, (ctype)(*[e for e in dataclass_value]))
        if hasattr(cvalue, "_fields_"):
            setattr(structure, cname, _dataclass_to_ctype(dataclass_value, hook))
    return structure


class DataClassCtypesMixIn(abc.ABC):
    """
    MixIn for dataclass to be able to convert from/to ctypes Structure/Union.
    """

    _cdata_endian: Endian
    """ The endian of the ctypes.Strcuture """

    _cdata_pack: int
    """ The maximum allignment of each field. Set into the ctypes.Strcuture._pack_ """

    @property
    def cdata_endian(self):
        return self.__class__._cdata_endian

    @property
    def cdata_pack(self):
        return self.__class__._cdata_pack

    @classmethod
    def ctype(cls: Type[T]) -> Type[Union[ctypes.Structure, ctypes.Union]]:
        """Return a ctypes.Strcuture/ctypes.Union class corresponding to own dataclass"""
        if cls._cdata_endian == Endian.BIG:
            return _create_ctype(cls, ctypes.BigEndianStructure, cls._cdata_pack)
        elif cls._cdata_endian == Endian.LITTLE:
            return _create_ctype(cls, ctypes.LittleEndianStructure, cls._cdata_pack)
        elif cls._cdata_endian == Endian.NATIVE:
            return _create_ctype(cls, ctypes.Structure, cls._cdata_pack)
        elif cls._cdata_endian == Endian.UNION:
            return _create_ctype(cls, ctypes.Union, cls._cdata_pack)

    @classmethod
    def from_buffer(cls: Type[T], buffer: bytearray) -> T:
        """Return a corresponding ctypes.Structure/ctypes.Union instance shared with given buffer."""
        structure = cls.ctype().from_buffer(buffer)
        return cls.from_ctype(structure)

    @classmethod
    def from_buffer_copy(cls: Type[T], buffer: bytes) -> T:
        """Return a corresponding ctypes.Structure/ctypes.Union instance copied from given buffer."""
        structure = cls.ctype().from_buffer_copy(buffer)
        return cls.from_ctype(structure)

    @classmethod
    def from_ctype(cls: Type[T], structure: CtypesStructuredData, hook: Optional[CtypesDecoderHook] = None) -> T:
        """Return an instance initialized with the given ctypes.Structure/ctypes.Union object."""
        return _ctype_to_dataclass(cls, structure, hook)

    def to_ctype(self: T, hook: Optional[CtypesEncoderHook] = None) -> CtypesStructuredData:
        """Return a ctypes.Strcuture instance from self."""
        return _dataclass_to_ctype(self, hook)

    @classmethod
    def from_dict(cls: Type[T], src: Dict[str, Any]) -> T:
        """Return an instance initialized with the given dict."""
        return cls(**src)

    def to_dict(self: T) -> Dict[str, Any]:
        """Return a dict instance from self."""
        return asdict(self)


class DataClassNativeEndianStructureMixIn(DataClassCtypesMixIn):
    _cdata_endian = Endian.NATIVE
    _cdata_pack = 1


class DataClassLittleEndianStructureMixIn(DataClassCtypesMixIn):
    _cdata_endian = Endian.LITTLE
    _cdata_pack = 1


class DataClassBigEndianStructureMixIn(DataClassCtypesMixIn):
    _cdata_endian = Endian.BIG
    _cdata_pack = 1


class DataClassUnionMixIn(DataClassCtypesMixIn):
    _cdata_endian = Endian.UNION
    _cdata_pack = 1
