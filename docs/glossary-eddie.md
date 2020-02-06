user query
==========
[user query]: #user-query


_also **query**, **search string**_.

How the user writes their _search intent_, as a series of Unicode code
points. This might be a messy, misspelled, strangely written string.
It is the job of the intelligent dictionary to take this wild thing
and make sense of it, returning results that satisfy the user's search
intent.


analysis
===================
[analysis]: #analysis
[analyses]: #analysis
[linguistic analysis]: #analysis
[linguistic breakdown]: #analysis

_also, **linguistic analysis** or **linguistic breakdown**_.

An **ordered** set of the [lemma][] and [morphosyntactic features][]
that can describe an [inflected wordform][wordform].

It _minimally_ consists of:

 - at least one [lemma][]
 - at least one feature, stating the wordform's [word class][]

### Example

One possible linguistic analysis of the [wordform][] "sabía" in
Spanish is:

    saber+V+Pst+Past+1Sg

In other words, the breakdown is:

 - It's a form of _saber_ (the lemma)
 - It's a _verb_
 - It's _past-tense_
 - It's actor is _first-person, singular_

Contains
--------

 - **1 or more** [lemmas][]
 - **1 or more** [morphosyntactic features][]

Describes
---------

 - **1** [wordform][]; note, a single **wordform** can have multiple
   distinct analyses.
