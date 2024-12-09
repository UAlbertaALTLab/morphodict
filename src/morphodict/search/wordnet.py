from morphodict.search.types import produce_entries, WordnetEntry
from morphodict.search.query import Query
from nltk.corpus import wordnet
from morphodict.lexicon.models import (
    WordNetSynset
)
class WordNetSearch:
    synsets : list[WordNetSynset]
    def __init__(self, query:Query) :
        canonical_query = "_".join(query.query_terms)
        self.synsets = list(WordNetSynset.objects.filter(
            name__in=produce_entries(" ".join(query.query_terms), wordnet.synsets(canonical_query))
        ))
        def ranking(synset: WordNetSynset) -> int :
            return WordnetEntry(synset.name).ranking()
        
        self.synsets.sort(key=ranking, reverse=True)
