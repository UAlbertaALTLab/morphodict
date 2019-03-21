# Copyright (C) 2018  Eddie Antonio Santos <easantos@ualberta.ca>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
from collections import ChainMap
from unicodedata import normalize


__all__ = ['sro2syllabics', 'syllabics2sro']
__version__ = '2019.2.18'


DEFAULT_HYPHENS = '\N{NARROW NO-BREAK SPACE}'

CONSONANT = '[ptkcshmnyw]|th'
STRICT_VOWEL = '[êioaîôâ]'
VOWEL = "{STRICT_VOWEL}|[eēī'’ōā]".format_map(globals())

# Match an SRO syllable.
sro_pattern = re.compile(r'''
    # A syllable that should be joined under the sandhi rule:
    # We're setting this up so that the onset (consonant and optional w) can
    # be glued together with the vowel. The parts are joined to
    # form one syllable, even though the intervening hyphen indicates that
    # they are in separate morphemes. That's sandhi!  See the front-matter in
    # Arok Wolvengrey's dictionary for more information and examples.
    #   Wolvengrey, Arok, ed. "ᓀᐦᐃᔭᐍᐏᐣ: ᐃᑗᐏᓇ / nēhiýawēwin: itwēwina/Cree:
    #   Words". Canadian Plains Research Center, October 2001. pp. xvi–xviii.

    ((?:{CONSONANT})w?)-({STRICT_VOWEL}) |

    # Listing all of the syllables.
    # NOTE: List the longer syllable first, since
    # the regular expression will match the first alternative that will
    # work—which must be the longest match!
    thê|thi|tho|tha|thî|thô|thâ                            |th|
    wê |wi |wo |wa |wî |wô |wâ                             |w |
    pê |pi |po |pa |pî |pô |pâ |pwê|pwi|pwo|pwa|pwî|pwô|pwâ|p |
    tê |ti |to |ta |tî |tô |tâ |twê|twi|two|twa|twî|twô|twâ|t |
    kê |ki |ko |ka |kî |kô |kâ |kwê|kwi|kwo|kwa|kwî|kwô|kwâ|k |
    cê |ci |co |ca |cî |cô |câ |cwê|cwi|cwo|cwa|cwî|cwô|cwâ|c |
    mê |mi |mo |ma |mî |mô |mâ |mwê|mwi|mwo|mwa|mwî|mwô|mwâ|m |
    nê |ni |no |na |nî |nô |nâ |nwê|nwa        |nwâ        |n |
    sê |si |so |sa |sî |sô |sâ |swê|swi|swo|swa|swî|swô|swâ|s |
    yê |yi |yo |ya |yî |yô |yâ |ywê|ywi|ywo|ywa|ywî|ywô|ywâ|y |
    h|l|r|
    ê|i|î|o|ô|a|â|
    -
'''.format_map(globals()), re.VERBOSE)


# A complete SRO to syllabics look-up table.
sro2syllabics_lookup = {
    "ê": "ᐁ", "i": "ᐃ", "î": "ᐄ", "o": "ᐅ", "ô": "ᐆ", "a": "ᐊ", "â": "ᐋ",
    "wê": "ᐍ", "wi": "ᐏ", "wî": "ᐑ", "wo": "ᐓ", "wô": "ᐕ", "wa": "ᐘ", "wâ": "ᐚ", "w": "ᐤ",
    "p": "ᑊ", "pê": "ᐯ", "pi": "ᐱ", "pî": "ᐲ", "po": "ᐳ", "pô": "ᐴ", "pa": "ᐸ", "pâ": "ᐹ",
    "pwê": "ᐻ", "pwi": "ᐽ", "pwî": "ᐿ", "pwo": "ᑁ", "pwô": "ᑃ", "pwa": "ᑅ", "pwâ": "ᑇ",
    "t": "ᐟ", "tê": "ᑌ", "ti": "ᑎ", "tî": "ᑏ", "to": "ᑐ", "tô": "ᑑ", "ta": "ᑕ", "tâ": "ᑖ",
    "twê": "ᑘ", "twi": "ᑚ", "twî": "ᑜ", "two": "ᑞ", "twô": "ᑠ", "twa": "ᑢ", "twâ": "ᑤ",
    "k": "ᐠ", "kê": "ᑫ", "ki": "ᑭ", "kî": "ᑮ", "ko": "ᑯ", "kô": "ᑰ", "ka": "ᑲ", "kâ": "ᑳ",
    "kwê": "ᑵ", "kwi": "ᑷ", "kwî": "ᑹ", "kwo": "ᑻ", "kwô": "ᑽ", "kwa": "ᑿ", "kwâ": "ᒁ",
    "c": "ᐨ", "cê": "ᒉ", "ci": "ᒋ", "cî": "ᒌ", "co": "ᒍ", "cô": "ᒎ", "ca": "ᒐ", "câ": "ᒑ",
    "cwê": "ᒓ", "cwi": "ᒕ", "cwî": "ᒗ", "cwo": "ᒙ", "cwô": "ᒛ", "cwa": "ᒝ", "cwâ": "ᒟ",
    "m": "ᒼ", "mê": "ᒣ", "mi": "ᒥ", "mî": "ᒦ", "mo": "ᒧ", "mô": "ᒨ", "ma": "ᒪ", "mâ": "ᒫ",
    "mwê": "ᒭ", "mwi": "ᒯ", "mwî": "ᒱ", "mwo": "ᒳ", "mwô": "ᒵ", "mwa": "ᒷ", "mwâ": "ᒹ",
    "n": "ᐣ", "nê": "ᓀ", "ni": "ᓂ", "nî": "ᓃ", "no": "ᓄ", "nô": "ᓅ", "na": "ᓇ", "nâ": "ᓈ",
    "nwê": "ᓊ", "nwa": "ᓌ", "nwâ": "ᓎ",
    "s": "ᐢ", "sê": "ᓭ", "si": "ᓯ", "sî": "ᓰ", "so": "ᓱ", "sô": "ᓲ", "sa": "ᓴ", "sâ": "ᓵ",
    "swê": "ᓷ", "swi": "ᓹ", "swî": "ᓻ", "swo": "ᓽ", "swô": "ᓿ", "swa": "ᔁ", "swâ": "ᔃ",
    "y": "ᕀ", "yê": "ᔦ", "yi": "ᔨ", "yî": "ᔩ", "yo": "ᔪ", "yô": "ᔫ", "ya": "ᔭ", "yâ": "ᔮ",
    "ywê": "ᔰ", "ywi": "ᔲ", "ywî": "ᔴ", "ywo": "ᔶ", "ywô": "ᔸ", "ywa": "ᔺ", "ywâ": "ᔼ",
    "th": "ᖮ", "thê": "ᖧ", "thi": "ᖨ", "thî": "ᖩ", "tho": "ᖪ", "thô": "ᖫ", "tha": "ᖬ", "thâ": "ᖭ",
    "l": "ᓬ", "r": "ᕒ", "h": "ᐦ", "hk": "ᕽ",
}


# These regular expressions are intended to strictly match Cree words
# We want to match *CREE* words, because we want to avoid accidentally
# transliterating words from other languages (e.g., English, French).
#
# These regular expressions are based on a HUGE simplification of Cree
# phonotactics—that is, how you glue sounds in the language together to make
# syllables and words, and what combinations sounds allowed and where.
#
# For more information, see:
# https://en.wikipedia.org/wiki/Plains_Cree#Phonotactics
WORD_INITIAL = r'''
    [ptkcmnsyh]w? |    # consonants that allow 'w' after
    (?:th|[rl]) |  # consonants that don't
    w |
    # can start with no consonant.
'''

WORD_MEDIAL = r'''
    # TODO: there should be a constraint that the constants cannot be
    # duplicated, but capturing groups won't work if these regex
    # snippets are concatenated into bigger regexes.
    (?:[hsmnwy]|th)? (?:[ptkcmnsyh]|th) w? |
    w |
    [yw]? [rl]  # for loan words
'''

WORD_FINAL = r'''
    [hs]? (?:[ptcksmnwy]|th) |
    h |
    [yw]? [rl]  # for loan word
    |  # can end with no consonant
'''

# NOTE: VOWEL is defined way near the top of the file.

CODA = 'th|[hs]?[ptkcmn]|h|s|y|w'
MORPHEME = r'''
    (?:{WORD_INITIAL}) (?:{VOWEL})
        (?: (?:{WORD_MEDIAL}) (?:{VOWEL}) )*
    (?:{WORD_FINAL})
'''.format_map(globals())

# TODO: DRY these up!
BEGIN_WORD = r'''
(?:
        ^  # Either the start of a string; or,
        |  # at the edge of "letters".
        (?<=[^a-zêioaîôâeēī'’ōā])
)
'''
END_WORD = r'''
(?:
        (?=[^a-zêioaîôâeēī'’ōā]) |
        $
)
'''

WORD = r'''
    # CODA before the hyphen to account for Sandhi.
    # It's possible to accept TWO codas using this formulation, but
    # I think that loss of precision is okay.
    {BEGIN_WORD} {MORPHEME} (?: (?:{CODA})?-{MORPHEME})* {END_WORD}
'''.format_map(globals())
word_pattern = re.compile(WORD, re.IGNORECASE | re.VERBOSE)

# This regex prevents matching EVERY period, instead only matching periods
# after Cree words, or, as an exception, as the only item in a string.
full_stop_pattern = re.compile(r'''
    (?<=[\u1400-\u167f])[.] |   # Match a full-stop after syllabics
    \A[.]\Z                     # or match as the only item.
''', re.VERBOSE)

# Converts macron and alternate forms of vowels into "canonical" forms.
TRANSLATE_ALT_FORMS = str.maketrans("eē'’īōā",
                                    "êêiiîôâ")


def sro2syllabics(sro: str,
                  hyphens: str = DEFAULT_HYPHENS,
                  sandhi: bool = True) -> str:
    r"""
    Convert Cree words written in SRO text to syllabics.

    Finds instances of SRO words in strings, and converts them all to
    syllabics.

    >>> sro2syllabics('Eddie nitisiyihkâson')
    'Eddie ᓂᑎᓯᔨᐦᑳᓱᐣ'

    You should be able to write words in Y-dialect (a.k.a., Plains Cree):

    >>> sro2syllabics('niya')
    'ᓂᔭ'

    ...and Th-dialect (a.k.a., Woods Cree):

    >>> sro2syllabics('nitha')
    'ᓂᖬ'

    Any word that does not have the "structure" of a Cree word is not
    converted:

    >>> sro2syllabics('Maskêkosihk trail')
    'ᒪᐢᑫᑯᓯᕽ trail'
    >>> sro2syllabics('Maskêkosihk tireyl')
    'ᒪᐢᑫᑯᓯᕽ ᑎᕒᐁᕀᓬ'

    Roman full-stops/periods (".") are converted into syllabics full-stops:

    >>> sro2syllabics('Eddie nitisiyihkâson.')
    'Eddie ᓂᑎᓯᔨᐦᑳᓱᐣ᙮'

    Note that the substitution of full-stops only takes place after syllabics;
    if it is obviously not Cree (like most English), it will not be converted:

    >>> sro2syllabics("tânisi. ninêhiyawân.")
    'ᑖᓂᓯ᙮ ᓂᓀᐦᐃᔭᐚᐣ᙮'
    >>> sro2syllabics("Howdy, English text.")
    'Howdy, English text.'

    ``sro2syllabics()`` can handle variations in orthography. For example,
    it can convert circumflexes (âêîô):

    >>> sro2syllabics('êwêpâpîhkêwêpinamahk')
    'ᐁᐍᐹᐲᐦᑫᐍᐱᓇᒪᕽ'

    It can convert macrons (āēīō):

    >>> sro2syllabics('ēwēpâpīhkēwēpinamahk')
    'ᐁᐍᐹᐲᐦᑫᐍᐱᓇᒪᕽ'

    And it can convert an unaccented "e" just as if it had the appropriate
    accent:

    >>> sro2syllabics('ewepapihkewepinamahk')
    'ᐁᐍᐸᐱᐦᑫᐍᐱᓇᒪᕽ'

    Additionally, apostrophes are interpreted as short-i's. For example,
    converting "tânsi" will not work as expected:

    >>> sro2syllabics("tânsi")
    'ᑖᐣᓯ'

    However, add an apostrophe after the 'n' and it will work correctly:

    >>> sro2syllabics("tân'si")
    'ᑖᓂᓯ'

    Hyphens
    -------

    Hyphens in Cree words are replaced with ``<U+202F NARROW NO-BREAK SPACE>``
    (NNBSP) by default. This is a space that is narrower than the normal space
    character. NNBSP also prevents breaking the word across line breaks. We
    chose the NNBSP character as the default, as it helps visually distinguish
    between meaningful sub-elements within words, while being less likely to
    be mistaken as word-separating whitespace by most text processing
    applications.

    Compare the following hyphen replacement schemes:

    ===================== ====================================
     Replace hyphens with  kâ-mahihkani-pimohtêt isiyihkâsow
    ===================== ====================================
     (nothing)             ᑳᒪᐦᐃᐦᑲᓂᐱᒧᐦᑌᐟ ᐃᓯᔨᐦᑳᓱᐤ
     NNBSP                 ᑳ ᒪᐦᐃᐦᑲᓂ ᐱᒧᐦᑌᐟ ᐃᓯᔨᐦᑳᓱᐤ
     Space                 ᑳ ᒪᐦᐃᐦᑲᓂ ᐱᒧᐦᑌᐟ  ᐃᓯᔨᐦᑳᓱᐤ
    ===================== ====================================

    We discourage using an ordinary space character (U+0020), as it is often
    interpreted as separating words, both by computers and people alike. If
    you are viewing this documentation in a web browser, try double clicking
    the syllabics rendition of "kâ-mahihkani-pimohtêt" with NNBSP separators
    versus the one with space separators. Double clicking typically selects an
    entire word by default, and this is often the case when double clicking
    the word with NNBSP characters; however this fails for the rendition with
    space characters.

    Despite this, you can chose any character of your liking to replace
    hyphens in syllabics by providing the ``hyphens=`` keyword argument:

    >>> sro2syllabics('kâ-mahihkani-pimohtêt', hyphens='\N{NARROW NO-BREAK SPACE}')
    'ᑳ ᒪᐦᐃᐦᑲᓂ ᐱᒧᐦᑌᐟ'
    >>> sro2syllabics('kâ-mahihkani-pimohtêt', hyphens='')
    'ᑳᒪᐦᐃᐦᑲᓂᐱᒧᐦᑌᐟ'
    >>> sro2syllabics('kâ-mahihkani-pimohtêt', hyphens=' ')
    'ᑳ ᒪᐦᐃᐦᑲᓂ ᐱᒧᐦᑌᐟ'

    Sandhi orthographic rule
    ------------------------

    In SRO, the most orthographically correct way to write certain compounds
    is to separate two *morphemes* with a hyphen. For example:

        | pîhc-âyihk — inside
        | nîhc-âyihk — outside

    However, both words are pronounced as if discarding the hyphen:

        | pîhcâyihk — inside
        | nîhcâyihk — outside

    This is called :term:`sandhi`.  When transliterated into syllabics,
    the transcription should follow the latter, blended interpretation, rather
    than the former, separated interpretation. By default, ``sro2syllabics()``
    applies the sandhi rule and joins the syllable as if there were no hyphen:

    >>> sro2syllabics('pîhc-âyihk')
    'ᐲᐦᒑᔨᕽ'

    However, if this is not desired, you can set ``sandhi=False`` as a keyword
    argument:

    >>> sro2syllabics('pîhc-âyihk', sandhi=False)
    'ᐲᐦᐨ ᐋᔨᕽ'

    :param str sro: the text with Cree words written in SRO.
    :param str hyphens: what to replace hyphens with
                        (default: ``<U+202F NARROW NO-BREAK SPACE>``).
    :param bool sandhi: whether to apply sandhi orthography rule (default:
                        ``True``).
    :return: the text with Cree words written in syllabics.
    :rtype: str
    """

    def transliterate_word(match) -> str:
        return transcode_sro_word_to_syllabics(match.group(0), hyphens, sandhi)

    # Replace each Cree word with its syllabics transliteration.
    transliteration = word_pattern.sub(transliterate_word, nfc(sro))
    # Replace Latin full-stops with syllabics full-stops.
    return full_stop_pattern.sub('\u166E', transliteration)


def transcode_sro_word_to_syllabics(sro_word: str, hyphen: str, sandhi: bool) -> str:
    """
    Transcribes one word at a time.
    """

    to_transcribe = sro_word.lower().\
        translate(TRANSLATE_ALT_FORMS)

    # Augment the lookup table with an entry for «-» so that we can replace
    # all instances of '-' easily.
    lookup = ChainMap({
        '-': hyphen
    }, sro2syllabics_lookup)

    parts = []

    match = sro_pattern.match(to_transcribe)
    while match:
        onset, vowel = match.groups()
        if sandhi and onset is not None:
            if onset.startswith('h'):
                # Special case for /hw?-V/ sandhi case:
                # add the 'h'/ᐦ syllabic, then proceed with the w?V as normal:
                parts.append('ᐦ')
                onset = onset[1:]
            # Apply sandhi rule
            assert vowel is not None
            syllable = onset + vowel
            next_syllable_pos = match.end()
        elif onset is not None:
            # Not Sandhi -- let's consume the onset (consonant)
            # Do NOT consume the labialized w!
            syllable = 'w' if onset == 'w' else onset.rstrip('w')
            # Skip the first consonant.
            next_syllable_pos = len(syllable)
            assert syllable in CONSONANT
        else:
            syllable = match.group(0)
            next_syllable_pos = match.end()

        # Get the syllabic
        syllabic = lookup[syllable]
        parts.append(syllabic)

        # Chop off transcribed part
        to_transcribe = to_transcribe[next_syllable_pos:]
        match = sro_pattern.match(to_transcribe)

    # Special-case word-final 'hk': we did not convert it in the above loop,
    # because it can only happen at the end of words, and if we did convert it
    # in the prior loop, it would convert '-ihkwê-' -> 'ᐃᕽᐍ' instead of 'ᐃᐦᑵ'
    # as intended. We know the end of the word is 'hk' because it got
    # converted to «ᐦ» followed by «ᐠ».
    if parts[-2:] == ['ᐦ', 'ᐠ']:
        parts[-2:] = [sro2syllabics_lookup['hk']]

    assert to_transcribe == '', 'could not transcribe %r' % (to_transcribe)
    return ''.join(parts)


def nfc(text):
    """
    Return NFC-normalized text.
    """
    return normalize('NFC', text)


# Derive the Syllabics -> SRO lookup table from the SRO -> Syllabics table.
syllabics2sro_lookup = {syl: sro for sro, syl in sro2syllabics_lookup.items()}
# Initially, no syllabics should map to an SRO string more than once
# (hence, the two tables should have an equal amount of entries).
assert len(syllabics2sro_lookup) == len(sro2syllabics_lookup)
# Add alternate and "look-alike" forms:
syllabics2sro_lookup.update({
    # Some communities use the ᐝ symbol instead of ᕀ for the y-final.
    # See:
    # https://en.wikipedia.org/w/index.php?title=Plains_Cree&oldid=848160114#Canadian_aboriginal_syllabics
    # for an explanation of this special y-final.
    '\N{CANADIAN SYLLABICS Y-CREE W}': 'y',

    # Convert ᙮ into a Latin full-stop.
    '\N{CANADIAN SYLLABICS FULL STOP}': '.',

    # Look-alikes characters:
    '\N{CANADIAN SYLLABICS T}': 'm',  # ᑦ looks like ᒼ or "m"
    '\N{CANADIAN SYLLABICS SAYISI YI}': 'hk',  # ᕁ looks like ᕽ or "hk"
    '\N{CANADIAN SYLLABICS FINAL PLUS}': 'y',  # ᐩ looks like ᕀ or "y"

    # Convert NNBSP within syllabics to hyphens to support round-trip
    # conversion between syllabics and SRO.
    '\N{NARROW NO-BREAK SPACE}': '-',
})

# Translation table to convert syllabics to SRO.
SYLLABICS_TO_SRO = str.maketrans(syllabics2sro_lookup)

# For use when converting SYLLABIC + FINAL MIDDLE DOT into the syllabic
# with a 'w'
SYLLABIC_WITH_DOT = {
    'ᐁ': 'ᐍ', 'ᐃ': 'ᐏ', 'ᐄ': 'ᐑ', 'ᐅ': 'ᐓ', 'ᐆ': 'ᐕ', 'ᐊ': 'ᐘ', 'ᐋ': 'ᐚ',
    'ᐯ': 'ᐻ', 'ᐱ': 'ᐽ', 'ᐲ': 'ᐿ', 'ᐳ': 'ᑁ', 'ᐴ': 'ᑃ', 'ᐸ': 'ᑅ', 'ᐹ': 'ᑇ',
    'ᑌ': 'ᑘ', 'ᑎ': 'ᑚ', 'ᑏ': 'ᑜ', 'ᑐ': 'ᑞ', 'ᑑ': 'ᑠ', 'ᑕ': 'ᑢ', 'ᑖ': 'ᑤ',
    'ᑫ': 'ᑵ', 'ᑭ': 'ᑷ', 'ᑮ': 'ᑹ', 'ᑯ': 'ᑻ', 'ᑰ': 'ᑽ', 'ᑲ': 'ᑿ', 'ᑳ': 'ᒁ',
    'ᒉ': 'ᒓ', 'ᒋ': 'ᒕ', 'ᒌ': 'ᒗ', 'ᒍ': 'ᒙ', 'ᒎ': 'ᒛ', 'ᒐ': 'ᒝ', 'ᒑ': 'ᒟ',
    'ᒣ': 'ᒭ', 'ᒥ': 'ᒯ', 'ᒦ': 'ᒱ', 'ᒧ': 'ᒳ', 'ᒨ': 'ᒵ', 'ᒪ': 'ᒷ', 'ᒫ': 'ᒹ',
    'ᓀ': 'ᓊ',                                         'ᓇ': 'ᓌ', 'ᓈ': 'ᓎ',
    'ᓭ': 'ᓷ', 'ᓯ': 'ᓹ', 'ᓰ': 'ᓻ', 'ᓱ': 'ᓽ', 'ᓲ': 'ᓿ', 'ᓴ': 'ᔁ', 'ᓵ': 'ᔃ',
    'ᔦ': 'ᔰ', 'ᔨ': 'ᔲ', 'ᔩ': 'ᔴ', 'ᔪ': 'ᔶ', 'ᔫ': 'ᔸ', 'ᔭ': 'ᔺ', 'ᔮ': 'ᔼ',
}
final_dot_pattern = re.compile(r'([{without_dot}])ᐧ'.format(
    without_dot=''.join(SYLLABIC_WITH_DOT.keys())
))

circumflex_to_macrons = str.maketrans('êîôâ',
                                      'ēīōā')


def syllabics2sro(syllabics: str, produce_macrons=False) -> str:
    r"""
    Convert Cree words written in syllabics to SRO.

    Finds all instances of syllabics in the given string, and converts it to
    SRO. Anything that is not written in
    syllabics is simply ignored:

    >>> syllabics2sro('Eddie ᓂᑎᓯᔨᐦᑳᓱᐣ᙮')
    'Eddie nitisiyihkâson.'

    You should be able to convert words written in Y-dialect (a.k.a., Plains Cree):

    >>> syllabics2sro('ᓂᔭ')
    'niya'

    ... and Th-dialect (a.k.a., Woods Cree):

    >>> syllabics2sro('ᓂᖬ')
    'nitha'

    By default, the SRO will be produced with circumflexes (âêîô):

    >>> syllabics2sro('ᐁᐍᐹᐲᐦᑫᐍᐱᓇᒪᕽ')
    'êwêpâpîhkêwêpinamahk'

    This can be changed to macrons (āēīō) by setting ``produce_macrons`` to
    ``True``:

    >>> syllabics2sro('ᐁᐍᐹᐲᐦᑫᐍᐱᓇᒪᕽ', produce_macrons=True)
    'ēwēpāpīhkēwēpinamahk'

    In both cases, the character produced will be a pre-composed character,
    rather than an ASCII character followed by a combining diacritical mark.
    That is, vowels are returned in *NFC normalization form*.

    For compatibility with :py:meth:`cree_sro_syllabics.sro2syllabics`,
    ``syllabics2sro`` will convert any instances of \<U+202F NARROW NO BREAK
    SPACE\> to a hyphen in the SRO transliteration.

    >>> syllabics2sro('ᑳ ᒪᐦᐃᐦᑲᓂ ᐱᒧᐦᑌᐟ')
    'kâ-mahihkani-pimohtêt'

    In some syllabics text, syllabics with a 'w' dot are rendered as two
    characters: the syllabic without the 'w' dot followed by \<U+1427 CANADIAN
    SYLLABICS FINAL MIDDLE DOT\>; this differs from the more appropriate
    pre-composed syllabic character with the 'w' dot. For example,

        | ᐃᑘᐏᓇ  --- pre-composed syllabic
        | ᐃᑌᐧᐃᐧᓇ --- syllabic + ``CANADIAN SYLLABICS FINAL MIDDLE DOT``

    ``syllabics2sro()`` can convert both cases appropriately:

    >>> syllabics2sro('ᐃᑘᐏᓇ')
    'itwêwina'
    >>> syllabics2sro('ᐃᑌᐧᐃᐧᓇ')
    'itwêwina'

    Some syllabics converters produce erroneous yet very similar looking
    characters. ``syllabics2sro()`` knows the following look-alike characters:

     ================================= ==================================
      Look-alike                        Correct character
     ================================= ==================================
      ᐩ CANADIAN SYLLABICS FINAL PLUS   ᕀ CANADIAN SYLLABICS WEST-CREE Y
      ᑦ CANADIAN SYLLABICS T            ᒼ CANADIAN SYLLABICS WEST-CREE M
      ᕁ CANADIAN SYLLABICS SAYISI YI    ᕽ CANADIAN SYLLABICS HK
     ================================= ==================================

    ``syllabics2sro()`` automatically interprets erroneous look-alikes as their
    visually equivalent characters.

    >>> syllabics2sro('ᒌᐯᐦᑕᑳᐧᐱᑲᐧᓂᐩ')
    'cîpêhtakwâpikwaniy'
    >>> syllabics2sro('ᐊᓴᒧᐱᑕᑦ')
    'asamopitam'
    >>> syllabics2sro('ᒫᒥᕁ')
    'mâmihk'

    :param str syllabics: the text with Cree words written in syllabics.
    :param produce_macrons: if ``True``, produces macrons (āēīō) instead of
                            circumflexes (âêîô).
    :return: the text with Cree words written in SRO.
    :rtype: str
    """

    def fix_final_dot(match):
        "Translate syllabic + FINAL MIDDLE DOT to syllabic with 'w'"
        return SYLLABIC_WITH_DOT[match.group(1)]

    # Normalize all SYLLABIC + FINAL MIDDLE DOT to the composed variant of the
    # syllabic.
    normalized = final_dot_pattern.sub(fix_final_dot, syllabics)
    # **AFTER** normalization, translate syllabics characters to SRO
    sro_string = normalized.translate(SYLLABICS_TO_SRO)

    if produce_macrons:
        return sro_string.translate(circumflex_to_macrons)
    return sro_string
