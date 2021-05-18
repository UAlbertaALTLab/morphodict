from typing import NamedTuple, Optional, Tuple

from CreeDictionary.utils.types import ConcatAnalysis


class Analysis(NamedTuple):
    """
    Analysis of a wordform.
    """

    raw_prefixes: str
    lemma: str
    raw_suffixes: str

    def concatenate(self) -> ConcatAnalysis:
        result = ""
        if self.raw_prefixes != "":
            result += self.raw_prefixes + "+"
        result += f"{self.lemma}+{self.raw_suffixes}"
        return ConcatAnalysis(result)


class XMLTranslation(NamedTuple):
    """
    Each instance corresponds to a <t></t> element inside <e></e>
    """

    text: str
    sources: Tuple[str, ...]


class XMLEntry(NamedTuple):
    """
    each instance represents an <e></e> element in the xml
    """

    # this element refers to a lexicon/lexical/dictionary entry
    # this is not necessarily a lemma in our FST's lexicon
    # which may be a lemma, or an non-lemma inflected form, or a normally non-inflecting phrase (with spaces).
    l: str

    # part of speech, a deprecated terminology. Roughly equivalent to "general word class"
    # all pos in crkeng.xml are (subject to change): {'', 'IPV', 'Pron', 'N', 'Ipc', 'V', '-'}
    pos: str

    # inflectional category, actually the <lc></lc> element (which means lexical category, a deprecated term)
    # Roughly equivalent to enums.InflectionalCategory
    # to be distinguished with "generated_ic" in DatabaseManager scripts
    # which means it's strictly from enums.InflectionalCategory
    # all <lc></lc> texts in crkeng.xml are (subject to change):
    # {'', 'NDA-1', 'NDI-?', 'NA-3', 'NA-4w', 'NDA-2', 'VTI-2', 'NDI-3', 'NDI-x', 'NDA-x',
    # 'IPJ  Exclamation', 'NI-5', 'NDA-4', 'VII-n', 'NDI-4', 'VTA-2', 'IPH', 'IPC ;; IPJ',
    # 'VAI-v', 'VTA-1', 'NI-3', 'VAI-n', 'NDA-4w', 'IPJ', 'PrI', 'NA-2', 'IPN', 'PR', 'IPV',
    # 'NA-?', 'NI-1', 'VTA-3', 'NI-?', 'VTA-4', 'VTI-3', 'NI-2', 'NA-4', 'NDI-1', 'NA-1', 'IPP',
    # 'NI-4w', 'INM', 'VTA-5', 'PrA', 'NDI-2', 'IPC', 'VTI-1', 'NI-4', 'NDA-3', 'VII-v', 'Interr'}
    ic: str

    # A lemma might has its stem specified. The stem can be used in the linguistic breakdown
    # e.g.., atim (NA) has the stem "atimw-". This would show up in the linguistic breakdown,
    # so breaking down "atimwak" would be: "atimw- + Noun + Animate + Plural".
    # e.g., maskwa (NA) has the stem "maskw-". so "your bear" kimaskom = your + "maskw-" + Noun + Animate + Singular.
    # e.g., nôhkom (NAD) has the stem "-ohkom-",
    # so "my grannies" nôhkomisak = my + -ohkom- + Noun + Animate + Dependent + Plural
    stem: Optional[str]

    # The translations of the entry in English
    translations: Tuple[XMLTranslation, ...]
