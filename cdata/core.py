import abc
import ctypes
import types
from dataclasses import asdict, fields, make_dataclass
from functools import lru_cache
from typing import Any, Dict, Optional, Type, TypeVar, get_type_hints

from . import metadata
from .type import (
    CTypeDecoder,
    CTypeEncoder,
    StructuredCType,
    StructuredCTypeClass,
)

_T = TypeVar("_T")
_S = TypeVar("_S", bound="CDataMixIn")

_DEFINED_CLASSES: Dict[str, Type] = {}


def _is_ctype_array(v: Any):
    return (
        isinstance(v, ctypes.Array)
        and hasattr(v, "_length_")
        and hasattr(v, "_type_")
    )


def _is_ctype_structure(v: Any):
    return isinstance(v, (ctypes.Structure, ctypes.Union)) and hasattr(
        v, "_fields_"
    )


def _get_metadata(
    data_class: Any, field_name: str, metadata_name: str
) -> Optional[Any]:
    return (
        [f for f in fields(data_class) if f.name == field_name]
        .pop()
        .metadata.get(metadata_name)
    )


def _get_encoder(data_class: Any, field_name: str) -> Optional[CTypeEncoder]:
    return _get_metadata(data_class, field_name, metadata.ENCODER)


def _get_decoder(data_class: Any, field_name: str) -> Optional[CTypeDecoder]:
    return _get_metadata(data_class, field_name, metadata.DECODER)


@lru_cache
def create_ctype_class(
    data_class: Type, base_ctype_class: StructuredCTypeClass, pack: int
) -> StructuredCTypeClass:
    """
    Create a class of ctypes.Structure corresponding to the given dataclass.
    """
    class_name = f"_generated_ctype_class_{data_class.__name__}"
    ctype_class = types.new_class(name=class_name, bases=(base_ctype_class,))
    setattr(ctype_class, "_pack_", pack)
    setattr(
        ctype_class,
        "_fields_",
        [(f.name, f.metadata.get(metadata.CTYPE)) for f in fields(data_class)],
    )
    # Cache the dataclass info for respective ctype class
    _DEFINED_CLASSES[class_name] = data_class

    return ctype_class


def dataclass_to_ctype(data_class_instance: Any) -> StructuredCType:
    """Create a ctypes.Structure instance from given dataclass instance."""
    ctype_instance = data_class_instance.__class__.ctype()()
    for fname, ftype in getattr(ctype_instance, "_fields_", []):
        fvalue = getattr(ctype_instance, fname)
        dataclass_value = getattr(data_class_instance, fname)
        encoder = _get_encoder(data_class_instance, fname)
        if encoder is not None:
            setattr(ctype_instance, fname, encoder(dataclass_value))
            continue
        elif _is_ctype_array(fvalue):
            if issubclass(fvalue._type_, (ctypes.Structure, ctypes.Union)):
                setattr(
                    ctype_instance,
                    fname,
                    (ftype)(
                        *[dataclass_to_ctype(elem) for elem in dataclass_value]
                    ),
                )
            else:
                setattr(
                    ctype_instance,
                    fname,
                    (ftype)(*[elem for elem in dataclass_value]),
                )
        elif _is_ctype_structure(fvalue):
            setattr(ctype_instance, fname, dataclass_to_ctype(dataclass_value))
        else:
            setattr(ctype_instance, fname, dataclass_value)
    return ctype_instance


@lru_cache
def create_dataclass(ctype_class: StructuredCTypeClass) -> Type:
    """
    Create a dataclass corresponding to the given ctypes.Structure.
    Return cached class information if it's already defined in create_ctype.
    """
    # Get class info if there is already a corresponding dataclass
    already_defined = _DEFINED_CLASSES.get(ctype_class.__name__)
    if already_defined is not None:
        return already_defined
    data_class = make_dataclass(
        cls_name=f"_generated_dataclass_{ctype_class.__name__}",
        fields=[
            (fname, ftype)
            for fname, ftype in getattr(ctype_class, "_fields_", [])
        ],
        bases=(CDataMixIn,),
    )
    return data_class


def ctype_to_dataclass(
    data_class: Type[_T],
    ctype_instance: StructuredCType,
) -> _T:
    """Create a dataclass instance initialized by ctypes.Structure"""
    d = {}
    for fname, _ in getattr(ctype_instance, "_fields_", []):
        fvalue = getattr(ctype_instance, fname)
        decoder = _get_decoder(data_class, fname)
        if decoder is not None:
            d[fname] = decoder(fvalue)
            continue
        elif _is_ctype_array(fvalue):
            if issubclass(fvalue._type_, (ctypes.Structure, ctypes.Union)):
                d[fname] = [
                    ctype_to_dataclass(create_dataclass(fvalue._type_), elem)
                    for elem in fvalue
                ]
            else:
                d[fname] = [elem for elem in fvalue]
        elif _is_ctype_structure(fvalue):
            d[fname] = ctype_to_dataclass(
                create_dataclass(fvalue.__class__), fvalue
            )
        else:
            d[fname] = fvalue
    return data_class(**d)


class CDataMixIn(abc.ABC):
    """
    MixIn for dataclass to be able to convert from/to ctypes Structure/Union.
    """

    _base_ctype_class_: StructuredCTypeClass
    """Base class of to create ctypes.Strcuture like instance."""

    _pack_: int
    """Maximum allignment of each field. Set to ctypes.Strcuture._pack_ """

    @classmethod
    def ctype(cls) -> StructuredCTypeClass:
        """Return a ctypes.Strcuture class corresponding to own dataclass"""
        return create_ctype_class(cls, cls._base_ctype_class_, cls._pack_)

    @classmethod
    def size(cls) -> int:
        """Return the size of corresponding dataclass"""
        return ctypes.sizeof(cls.ctype())

    @classmethod
    def from_ctype(
        cls: Type[_S],
        ctype_instance: StructuredCType,
    ) -> _S:
        """Return an instance initialized with the given ctypes.Structure."""
        return ctype_to_dataclass(cls, ctype_instance)

    def to_ctype(self) -> StructuredCType:
        """Return a ctypes.Strcuture instance from self."""
        return dataclass_to_ctype(self)

    @classmethod
    def from_dict(cls: Type[_S], src: Dict[str, Any]) -> _S:
        """Return an instance initialized with the given dict."""
        kwargs = {}
        field_dict = {field.name: field for field in fields(cls)}
        field_type_dict = get_type_hints(cls)
        for k, v in src.items():
            field = field_dict[k]
            field_type = field_type_dict[field.name]
            if isinstance(v, dict) and issubclass(field_type, CDataMixIn):
                kwargs[k] = field_type.from_dict(v)
            elif isinstance(v, list):
                type_of_list_element = field_type.__args__[0]
                if issubclass(type_of_list_element, CDataMixIn):
                    kwargs[k] = [type_of_list_element.from_dict(e) for e in v]
                else:
                    kwargs[k] = v
            else:
                kwargs[k] = v
        return cls(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Return a dict instance from self."""
        return asdict(self)

    @classmethod
    def from_buffer(cls: Type[_S], buffer: bytearray) -> _S:
        """Return a corresponding ctypes  instance shared with given buffer."""
        structure = cls.ctype().from_buffer(buffer)
        return cls.from_ctype(structure)

    def to_bytearray(self) -> bytes:
        """Serialize the data into bytearray."""
        return bytearray(self.to_ctype())

    @classmethod
    def from_buffer_copy(cls: Type[_S], buffer: bytes) -> _S:
        """Return a corresponding ctypes  instance copied from given buffer."""
        structure = cls.ctype().from_buffer_copy(buffer)
        return cls.from_ctype(structure)

    def to_bytes(self) -> bytes:
        """Serialize the data into bytes."""
        return bytes(self.to_ctype())


class NativeEndianCDataMixIn(CDataMixIn):
    _base_ctype_class_ = ctypes.Structure
    _pack_ = 1


class LittleEndianCDataMixIn(CDataMixIn):
    _base_ctype_class_ = ctypes.LittleEndianStructure
    _pack_ = 1


class BigEndianCDataMixIn(CDataMixIn):
    _base_ctype_class_ = ctypes.BigEndianStructure
    _pack_ = 1


class UnionCDataMixIn(CDataMixIn):
    _base_ctype_class_ = ctypes.Union
    _pack_ = 1
