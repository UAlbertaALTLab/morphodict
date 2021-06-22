import pytest

from morphodict.lexicon.util import to_source_language_keyword


@pytest.mark.parametrize(
    ("input", "expected"),
    [
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
