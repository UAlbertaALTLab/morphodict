from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import Synset
from collections.abc import Iterable
import re

format_regexp = r'^\s*\((?P<pos>\w+)\)\s+(?P<stem>[^\s]+)\s*\#\s*(?P<num>\d+)\s*\Z'

def wordnet_for_nltk(keyword: str) -> str:
    matches = re.match(format_regexp, keyword)
    if matches:
        return matches['stem']+'.'+matches['pos']+'.'+matches['num']
    return keyword

class WordnetEntry:

    synset: Synset
    def __init__ (self, entry:str, nltk_format=False):
        self.synset = wn.synset(
            entry if nltk_format else wordnet_for_nltk(entry))
    
    def __str__ (self):
        data = self.synset.name().split(".")
        entry = ".".join(data[0:-2])
        return f"({data[-2]}) {entry}#{int(data[-1])}"
    
    def hyponyms(self):
        return produce_entries(self.synset.hyponyms())
    
    def hypernyms(self):
        return produce_entries(self.synset.hyponyms())
    
    def member_holonyms(self):
        return produce_entries(self.synset.member_holonyms())
    
    

def produce_entries(entries:Iterable[Synset]) -> list[WordnetEntry]:
    return [WordnetEntry(e, nltk_format=True) for e in entries]