# Created by Matt

# The database had two forms of preverbs existing, one with dash, one without
# e.g. "e" and "ê-" coexist in the database,
# "e" has definition from MD and "ê-" has definition from CW. They should be merged
# e.g. "mayi" from MD and "mâyi-" from CW coexist in the database
# preverbs in MD typically does not have circumflexes and do not have dashes

# this migration merges these preverbs and standardize both "full-lc" and "pos" to IPV
# this migration is conservative and tries to not err by merging when very sure.

# this migration also appends dashes to all preverbs when absent

from collections import defaultdict
from typing import Dict, Optional, Tuple, List, Set

from django.db import migrations, models
from django.db.models import Q

from utils.cree_lev_dist import remove_cree_diacritics


def merge_preverbs(apps, schema_editor):
    """
    From the sources field, creates citations.
    """

    Wordform = apps.get_model("API", "Wordform")

    # group preverbs
    no_dash_asciis_to_wordforms: Dict[str, Set[Wordform]] = defaultdict(set)
    for preverb_wordform in Wordform.objects.filter(Q(full_lc="IPV") | Q(pos="IPV")):
        no_dash_ascii = remove_cree_diacritics(preverb_wordform.text.strip("-"))
        no_dash_asciis_to_wordforms[no_dash_ascii].add(preverb_wordform)

    # merge to the wordform object with dash, assume the wordform with dash is correct (as it's from CW)
    for no_dash_ascii, wordforms in no_dash_asciis_to_wordforms.items():

        dashed_wordforms = {wf for wf in wordforms if wf.text.endswith("-")}
        dashed_count = len(dashed_wordforms)
        if (
            dashed_count == 0 or dashed_count >= 2
        ):  # dashed_count == 0 means it's a MD only preverb. Leave it there. They will be filtered out in the search
            # page as it's not standardized

            if dashed_count >= 2:
                # dashed_count >= 2:
                # e.g. "maci-" and "mâci-" are both in the database, they mean different things
                print(
                    "these preverbs might have different meanings and they require manual verification."
                    " Merging is not performed:",
                    [wf.text for wf in dashed_wordforms],
                )
            # append dashes to everything
            for wf in wordforms:
                if not wf.text.endswith("-"):
                    wf.text += "-"
                    wf.save()
            continue

        dashed_wordform = dashed_wordforms.pop()  # dashed_wordforms has length 1
        wordforms.remove(dashed_wordform)

        # normalized full_lc and pos
        dashed_wordform.full_lc = "IPV"
        dashed_wordform.pos = "IPV"
        dashed_wordform.save()

        existing_definition_texts: Set[str] = {
            d.text for d in dashed_wordform.definitions.all()
        }

        # merge definition of all others and delete them
        for wordform in wordforms:
            for definition_to_be_merged in wordform.definitions.all():
                if definition_to_be_merged.text not in existing_definition_texts:
                    definition_to_be_merged.wordform = dashed_wordform
                    definition_to_be_merged.save()
            wordform.delete()
            print(f"wordform {wordform.text} merged to {dashed_wordform.text}")


class Migration(migrations.Migration):

    dependencies = [
        ("API", "0006_auto_20200205_0256"),
    ]
    operations = [migrations.RunPython(merge_preverbs)]
