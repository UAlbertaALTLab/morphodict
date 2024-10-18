from typing import NewType, TypeVar, Optional

from typing_extensions import Protocol

# analysis but concatenated
Label = NewType("Label", str)
FSTTag = NewType("FSTTag", str)
FSTLemma = NewType("FSTLemma", str)
ConcatAnalysis = NewType("ConcatAnalysis", str)

NamedTupleFieldName = NewType("NamedTupleFieldName", str)

# HashableNamedTupleFieldValue = NewType("HashableNamedTupleFieldValue", Hashable) doesn't really work


class HashableNamedTupleFieldValue(Protocol):
    def __hash__(self): ...


T = TypeVar("T")


# From https://github.com/python/typing/issues/645#issuecomment-501057220
def cast_away_optional(arg: Optional[T]) -> T:
    assert arg is not None
    return arg
