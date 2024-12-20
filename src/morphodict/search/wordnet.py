from morphodict.search.types import produce_entries, WordnetEntry
from morphodict.search.query import Query
from nltk.corpus import wordnet
from morphodict.lexicon.models import WordNetSynset
from morphodict.phrase_translate.types import PhraseAnalyzedQuery


class WordNetSearch:
    synsets: list[WordNetSynset]
    analyzed_query: PhraseAnalyzedQuery | None

    def __init__(self, query: Query):
        self.analyzed_query = None
        inflected = PhraseAnalyzedQuery(" ".join(query.query_terms))
        if 1 < len(query.query_terms) and inflected.filtered_query:
            canonical_query = inflected.filtered_query.split(" ")
            self.analyzed_query = inflected
        else:
            canonical_query = query.query_terms
        lemmas = wordnet.synsets("_".join(canonical_query))
        candidate_infinitive = [x.removesuffix("s") for x in canonical_query]
        if lemmas != candidate_infinitive:
            lemmas.extend(wordnet.synsets("_".join(candidate_infinitive)))
        self.synsets = list(
            WordNetSynset.objects.filter(
                name__in=produce_entries(" ".join(canonical_query), lemmas)
            )
        )

        def ranking(synset: WordNetSynset) -> int:
            return WordnetEntry(synset.name).ranking()

        self.synsets.sort(key=ranking, reverse=True)
