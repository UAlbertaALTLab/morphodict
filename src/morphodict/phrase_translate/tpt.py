from tsuutina_phrase_translation import EnglishGenerator  # type: ignore
from morphodict.utils.types import FSTTag

generator = EnglishGenerator()


def tsuutina_inflect_target_phrase(
    tags_for_phrase: tuple[FSTTag, ...], lemma_definition: str, extra_args: dict
) -> str:
    candidates: list[str] = generator.apply(
        "", "".join(tags_for_phrase), lemma_definition, **extra_args
    )
    return ", ".join(candidates) if candidates else ""
