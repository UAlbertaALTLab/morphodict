from typing import NewType, TypeVar, Optional

from typing_extensions import Protocol

# analysis but concatenated
Label = NewType("Label", str)
FSTTag = NewType("FSTTag", str)
FSTLemma = NewType("FSTLemma", str)
ConcatAnalysis = NewType("ConcatAnalysis", str)
