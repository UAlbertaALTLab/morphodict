
  - Iff analysis is null, the source-language headword will be indexed for
    fuzzy search, which currently means allowing search with missing
    diacritics, or leading/trailing hyphens.

    The assumption here is that if the headword is analyzable, the relaxed
    analyzer FST will take care of any lookup needs.

