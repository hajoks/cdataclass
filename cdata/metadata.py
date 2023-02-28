from typing import Any, Dict, Optional

from .type import CTypeClass, CTypeDecoder, CTypeEncoder

MetaData = Dict[str, Any]

CTYPE = "ctype"
DECODER = "decoder"
ENCODER = "encoder"


def meta(
    ctype: CTypeClass,
    *,
    encoder: Optional[CTypeEncoder] = None,
    decoder: Optional[CTypeDecoder] = None,
) -> MetaData:
    """Create a map of cdata related metadata.

    e.g.

    @cdata.little
    @dataclasses.dataclass
    class Sample:
        string: str = field(
            metadata=meta(
                ctypes.c_char * 5,
                decoder=lambda v: v.decode("utf-8"),
                encoder=lambda v: v.encode("utf-8"),
            )
        )

    Args:
        ctype (CTypeClass):\
              ctypes class the field should use for encoding/decoding.
        encoder (Optional[CTypeEncoder], optional):\
              Callback for encoding the python object to ctypes object.\
              Defaults to None.
        decoder (Optional[CTypeDecoder], optional):\
              Callback for decoding the ctypes object to python object.\
              Defaults to None.

    Returns:
        MetaData (Dict[str, Any]): Map of metadata.\
            Should be passed to "metadata" arg of dataclasses.field.
    """
    d: MetaData = {}
    d[CTYPE] = ctype
    if decoder is not None:
        d[DECODER] = decoder
    if encoder is not None:
        d[ENCODER] = encoder
    return d
