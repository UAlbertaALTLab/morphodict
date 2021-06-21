import pytest

from morphodict.lexicon.util import strip_accents_for_search_lookups


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
    assert strip_accents_for_search_lookups(input) == expected
