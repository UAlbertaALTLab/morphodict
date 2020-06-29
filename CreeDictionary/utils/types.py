from typing import NewType, Protocol

# analysis but concatenated
Label = NewType("Label", str)
FSTTag = NewType("FSTTag", str)
FSTLemma = NewType("FSTLemma", str)
ConcatAnalysis = NewType("ConcatAnalysis", str)

NamedTupleFieldName = NewType("NamedTupleFieldName", str)

# NamedTupleFieldValue = NewType("NamedTupleFieldName", Hashable) doesn't really work


class NamedTupleFieldValue(Protocol):
    def __hash__(self):
        ...
