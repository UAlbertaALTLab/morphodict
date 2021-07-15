import pytest

from morphodict.lexicon.util import to_source_language_keyword

COMBINING_CIRCUMFLEX = "̂"
COMBINING_MACRON = "̄"


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ("Wâpamêw", "wapamew"),
        ("âêîôû", "aeiou"),
        (
            f"a{COMBINING_CIRCUMFLEX}e{COMBINING_CIRCUMFLEX}i{COMBINING_CIRCUMFLEX}o{COMBINING_CIRCUMFLEX}u{COMBINING_CIRCUMFLEX}",
            "aeiou",
        ),
        ("ÂÊÎÔÛ", "aeiou"),
        (
            f"A{COMBINING_CIRCUMFLEX}E{COMBINING_CIRCUMFLEX}I{COMBINING_CIRCUMFLEX}O{COMBINING_CIRCUMFLEX}U{COMBINING_CIRCUMFLEX}",
            "aeiou",
        ),
        ("āēīōū", "aeiou"),
        ("ĀĒĪŌŪ", "aeiou"),
        (
            f"a{COMBINING_MACRON}e{COMBINING_MACRON}i{COMBINING_MACRON}o{COMBINING_MACRON}u{COMBINING_MACRON}",
            "aeiou",
        ),
        (
            f"A{COMBINING_MACRON}E{COMBINING_MACRON}I{COMBINING_MACRON}O{COMBINING_MACRON}U{COMBINING_MACRON}",
            "aeiou",
        ),
        ("ý", "y"),
        ("Gūnáhà", "gunaha"),
        ("ììdììtɫō", "iidiitlo"),
        # Note that the lowercase has a different character for the final sigma
        ("ΣΟΦΌΝ ΤῸ ΣΑΦΈΣ", "σοφον το σαφες"),
        ("hello", "hello"),
        ("hellø", "hello"),
        ("hełło", "hello"),
        ("hêllò", "hello"),
        ("hěllo", "hello"),
        (
            "h̷̨̨̢̝̺̥͕̦̘̺̥̖̺̐ͅe̶̢̛͙̱͔̗͓͓̊̇̓̍̈́͐͋̍̐͑͌̌̿͘͜͠͝͝ļ̴̨̧͔̭̲̲͎̘̱̬̼͉̜̱̤͎̹̞̝̥̲̙̙̮̪̖̽̓̌͊̊̍̆́̎̑͌̇̓̈́́͊͌̾̆̿͊̎͌̈̕̕͜͠ͅl̸̨̧͓̭̻̝͖͕̪͖̩̯̞͙͖͙̦͈̘̥̱̩̫̬̎̈́͗̓̑̎̾͋̍̏͒̽̃̕͠ǒ̵͔̯̜̣̘̹̑͜͝",
            "hello",
        ),
    ],
)
def test_strip_accents_for_search_lookups(input, expected):
    assert to_source_language_keyword(input) == expected
