import ctypes
from typing import Any, Callable, Optional, Type, Union

AcceptableCtype = Union[ctypes.Structure, ctypes._SimpleCData, ctypes._Pointer, ctypes.Union, ctypes.Array]

CFieldName = str

CFieldType = Any

CFliedValue = Any

DataclassValue = Any

CtypesEncoderHook = Callable[[CFieldName, CFieldType, CFliedValue, DataclassValue], Optional[Any]]

CtypesDecoderHook = Callable[[CFieldName, CFieldType, CFliedValue], Optional[Any]]

CtypesStructuredType = Union[Type[ctypes.Structure], Type[ctypes.Union]]

CtypesStructuredData = Union[ctypes.Structure, ctypes.Union]

StructureName = str
