from morphodict.phrase_translate.to_target import inflect_target_language_phrase
from morphodict.search.types import produce_entries, WordnetEntry
from morphodict.search.query import Query
from morphodict.search.core import SearchResults
from nltk.corpus import wordnet
from morphodict.lexicon.models import WordNetSynset
from morphodict.analysis import RichAnalysis
from morphodict.search.espt import EsptSearch
from morphodict.phrase_translate.tag_maps import (
    source_noun_tags,
)
from morphodict.phrase_translate.definition_cleanup import (
    cleanup_target_definition_for_translation,
)


class WordNetSearch:
    synsets: list[WordNetSynset]

    espt: EsptSearch | None

    def __init__(self, query: Query):
        self.espt = None
        canonical_query: list[str] = query.query_terms
        if 1 < len(query.query_terms):
            self.espt = EsptSearch(query, SearchResults())
            self.espt.convert_search_query_to_espt()
            if not self.espt.query_analyzed_ok:
                self.espt = None
            else:
                canonical_query = self.espt.query.query_terms
        lemmas = wordnet.synsets("_".join(canonical_query))
        candidate_infinitive = [x.removesuffix("s") for x in canonical_query]
        if canonical_query != candidate_infinitive:
            lemmas.extend(wordnet.synsets("_".join(candidate_infinitive)))
        self.synsets = list(
            WordNetSynset.objects.filter(
                name__in=produce_entries(" ".join(canonical_query), lemmas)
            )
        )

        def ranking(synset: WordNetSynset) -> int:
            return WordnetEntry(synset.name).ranking()

        self.synsets.sort(key=ranking, reverse=True)

    def inflect_wordnet_definition(self, wn_entry: WordnetEntry) -> str:
        if self.espt:
            results: list[str] = []
            orig_tags_starting_with_plus: list[str] = []
            tags_ending_with_plus: list[str] = []
            if self.espt.tags:
                for t in self.espt.new_tags:
                    if t.startswith("+"):
                        orig_tags_starting_with_plus.append(t)
                    else:
                        tags_ending_with_plus.append(t)
                    tags_starting_with_plus = orig_tags_starting_with_plus[:]
                    noun_tags = []
                    if "+N" in self.espt.tags:
                        noun_tags = [
                            tag for tag in self.espt.tags if tag in source_noun_tags
                        ]
                        if "+N" in tags_starting_with_plus:
                            tags_starting_with_plus.remove("+N")
                        if "+Der/Dim" in tags_starting_with_plus:
                            # noun tags need to be repeated in this case
                            insert_index = tags_starting_with_plus.index("+Der/Dim") + 1
                            tags_starting_with_plus[insert_index:insert_index] = (
                                noun_tags
                            )

                analysis = RichAnalysis(
                    (
                        tags_ending_with_plus,
                        "",
                        noun_tags + tags_starting_with_plus,
                    )
                )

                for phrase in wn_entry.definition().split(";"):
                    clean_phrase = cleanup_target_definition_for_translation(phrase)
                    tags_starting_with_plus = orig_tags_starting_with_plus[:]
                    result = inflect_target_language_phrase(
                        analysis, clean_phrase
                    ) or inflect_target_language_phrase(analysis, "to " + clean_phrase)
                    if result:
                        results.append(result)
                    else:
                        results.append(phrase)
                return ";".join(results)

        return wn_entry.definition()
