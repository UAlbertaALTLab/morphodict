"""
Preferences used in itwêwina, the Cree Intelligent Dictionary.
"""
from django.conf import settings

from morphodict.preference import register_preference, Preference


@register_preference
class DisplayMode(Preference):
    """
    What style labels should be used in the paradigm?
    """

    cookie_name = "display_mode"
    choices = {
        # Plain English labels; e.g., I → You (one), Something is happening now
        "english": "Plain English labels",
        # (Short) linguistic labels; e.g., 1Sg → 2Sg, Present Tense
        "linguistic": "Linguistic labels",
        # nêhiyawêwin labels; e.g., niya → kiya, mêkwâc
        "source_language": settings.MORPHODICT_LANGUAGE_ENDONYM + " labels",
    }
    default = "english"


@register_preference
class AnimateEmoji(Preference):
    """
    Which emoji to use to substitute all animate emoji (awa words).
    """

    # Ensure the internal name and the cookie name (external name) are the same!
    name = "animate_emoji"
    cookie_name = name

    default = "iyiniw"  # the original itwêwina animate emoji
    choices = {
        "iyiniw": "🧑🏽",  # iyiniw (NA)/tastawiyiniw (NA)
        "granny": "👵🏽",  # kôhkom/*kokum (NDA)
        "grandpa": "👴🏽",  # môsom/*moshum (NDA)
        # Required by requester of this feature:
        "wolf": "🐺",  # mahihkan (NA)
        # Required for community partner
        "bear": "🐻",  # maskwa (NA)
        # Counter-intuitive awa word:
        "bread": "🍞",  # pahkwêsikan (NA)
        # Significant awa word:
        "star": "🌟",  # atâhk/acâhkos (NA)
        # I don't want to add too many options to start with, but more can always be
        # added in the future like:
        # - 🦬 paskwâwi-mostsos
        # - 🦫 amisk
    }


@register_preference
class DictionarySource(Preference):
    """
    Which dictionaries should be included in the search results?
    """

    cookie_name = "dictionary_source"
    choices = {
        "cw": "Show entries from the Cree: Words dictionary. Wolvengrey, Arok, editor. Cree: Words. Regina, University of Regina Press, 2001",
        "md": "Show entries from the Maskwacîs Dictionary. Maskwacîs Dictionary. Maskwacîs, Maskwachees Cultural College, 1998.",
        "aecd": "Show entries from the Alberta Elders' Cree Dictionary/alberta ohci kehtehayak nehiyaw otwestamâkewasinahikan compiled by Nancy LeClaire and George Cardinal, edited by Earle H. Waugh. Edmonton: University of Alberta Press, 2002.",
        "all": "Show entries from CW, AECD, and MD (default)",
    }

    default = "all"


@register_preference
class AudioSource(Preference):
    """
    Which dictionaries should be included in the search results?
    """

    cookie_name = "audio_source"
    choices = {
        "maskwacis": ["Maskwacîs", "Show audio from the Maskwacîs Cree community"],
        "moswacihk": ["mōswacīhk", "Show audio from the mōswacīhk community (White Bear First Nations, Saskatchewan"],
        "both": ["Both", "Show audio from both sources (default)"],
    }

    default = "both"


@register_preference
class ShowEmoji(Preference):
    """
    Which dictionaries should be included in the search results?
    """

    cookie_name = "show_emoji"
    choices = {
        "yes": "Show emojis with my entries (default)",
        "no": "Don't show emojis with my entries",
    }

    default = "yes"


@register_preference
class ShowMorphemes(Preference):
    """
    Which dictionaries should be included in the search results?
    """

    cookie_name = "show_morphemes"
    choices = {
        "everywhere": "I would like to see morpheme boundaries in entry headers and in paradigm tables",
        "headers": "I would like to see morpheme boundaries in headers only",
        "paradigm": "I would like to see morpheme boundaries in paradigm tables only",
        "nowhere": "I do not want to see morpheme boundaries (default)",
    }

    default = "nowhere"


@register_preference
class ParadigmAudio(Preference):
    """
    Should we show audio in the paradigms?
    """

    cookie_name = "paradigm_audio"
    choices = {
        "yes": "I would like to see audio in paradigm layouts",
        "no": "I do not want to see audio in paradigm layouts",
    }
    default = "no"


@register_preference
class SynthesizedAudio(Preference):
    """
    Should we show synthesized audio?
    """

    cookie_name = "synthesized_audio"
    choices = {
        "yes": "I would like to hear synthesized recordings",
        "no": "I do not want to hear synthesized recordings",
    }
    default = "no"


@register_preference
class SynthesizedAudioInParadigm(Preference):
    """
    Should we show synthesized audio in the paradigms?
    """

    cookie_name = "synthesized_audio_in_paradigm"
    choices = {
        "yes": "I would like to hear synthesized recordings in my paradigm layouts",
        "no": "I do not want to hear synthesized recordings in my paradigm layouts",
    }
    default = "no"


@register_preference
class ShowInflectionalCategory(Preference):
    """
    Should we show synthesized audio in the paradigms?
    """

    cookie_name = "show_inflectional_category"
    choices = {
        "yes": "I always want to see the inflectional category",
        "no": "I only want to see the inflectional category in linguistic mode",
    }
    default = "yes"


@register_preference
class InflectEnglishPhrase(Preference):
    """
    Should we show synthesized audio in the paradigms?
    espt: t
    """

    cookie_name = "inflect_english_phrase"
    choices = {
        "yes": "Generate Cree word-forms matching simple English verb or noun phrases",
        "no": "Only show dictionary entry headwords as they are",
    }
    default = "yes"


@register_preference
class AutoTranslateDefs(Preference):
    """
    Should we show synthesized audio in the paradigms?
    auto: t
    """

    cookie_name = "auto_translate_defs"
    choices = {
        "yes": "Generate English definitions matching core Cree word-forms",
        "no": "Only show dictionary definitions as they are",
    }
    default = "yes"
