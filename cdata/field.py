import dataclasses
from typing import Any, Optional

from .type import AcceptableCtype, CtypesDecoderHook, CtypesEncoderHook


def field(
    ctype: AcceptableCtype,
    default: Any = None,
    *,
    decoder: Optional[CtypesDecoderHook] = None,
    encoder: Optional[CtypesEncoderHook] = None,
    **kwargs: Any,
) -> dataclasses.Field:
    """
    Return dataclasses.Field instance adding some attributes to its metadata.
    """
    metadata = {}
    metadata.update(kwargs)

    metadata["ctype"] = ctype

    if default is not None:
        if hasattr(metadata["ctype"], "_length_"):
            array_length = getattr(metadata["ctype"], "_length_")
            if array_length is not None and array_length < len(default):
                raise ValueError(
                    f"The length of default value for {ctype} field must be equall or less than {array_length}"
                )
        metadata["default"] = default

    if encoder is not None:
        metadata["decoder"] = decoder

    if decoder is not None:
        metadata["encoder"] = encoder

    if isinstance(default, (list, dict, set)):
        return dataclasses.field(
            default_factory=lambda: default,
            metadata=metadata,
        )
    else:
        return dataclasses.field(
            default=default,
            metadata=metadata,
        )
