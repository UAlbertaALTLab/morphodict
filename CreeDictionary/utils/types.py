from typing import NewType
from typing_extensions import Protocol

# analysis but concatenated
Label = NewType("Label", str)
FSTTag = NewType("FSTTag", str)
FSTLemma = NewType("FSTLemma", str)
ConcatAnalysis = NewType("ConcatAnalysis", str)

NamedTupleFieldName = NewType("NamedTupleFieldName", str)

# HashableNamedTupleFieldValue = NewType("HashableNamedTupleFieldValue", Hashable) doesn't really work


class HashableNamedTupleFieldValue(Protocol):
    def __hash__(self):
        ...
