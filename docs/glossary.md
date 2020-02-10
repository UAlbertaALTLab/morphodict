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


definition
==========
[definition]: #definition
[definitions]: #definition

One of possibly several meanings of the [head][].

Part of
-------

-   **1** [dictionary entry][]

Describes
---------

*  **1** [head][]


dictionary entry
================
[dictionary entry]: #dictionary-entry

The main content of a [dictionary][]. Consists of
the [head][] (in one or more [orthothographical][]
representations), the [word class][], and the
[definitions][].

Part of
-------

-   **1** [dictionary][]

Contains
--------

-   **1** [head][]
-   **1** or more [definitions][]
-   **1** [word class][], if the [head][] is a [word form][]


indeclinable particle
=====================
[indeclinable particle]: #indeclinable-particle
[Ipc]: #indeclinable-particle

(In Plains Cree linguistics) The word class of [terms][] that do not
[inflect][]. Often abbreviated as [Ipc].

Is a
----

-   [word class][]


inflectional category
=====================
[inflectional category]: #inflectional-category
[inflectional categories]: #inflectional-category

A more detailed categorization of a [word class][],
things that belong to the same inflection category inflects similarly

Examples
--------

-   NI-1
-   VTA-n
-   NDA-4w


general word class
=====================
[general word class]: #general-word-class

Superclass of [word class][]. Does not contain
[inflectional categories][]. Similar
to [part of speech][].

General word classes are are not detailed
enough to tell you how its members [inflect]. A [specific word class][], on the
other hand, tells you enough to be able to [inflect].

Consists of
-----------

-   **1 or more** [word classes][]

In Plains Cree
--------------

* [Noun][] — use the four word classes instead: [NI], [NA], [NID], [NAD]
* [Verb][] — use the four word classes instead: [VII], [VAI], [VTI], [VTA]


head
====
[head]: #head

The highest level structure of a [dictionary][].
Each head is listed alphabetically (with derivations (phrases on the
[wordform][]) coming after the \'root\' listing).


Lemma
-----
[lemma]: #lemma
[lemmas]: #lemma
[lemmata]: #lemma

The base form of a [word form]; the form chosen to depict the basic representation of the paradigm. Often the least structurally and semantically marked form.  Unlike a [stem] or [root], a lemma is always a [word form].

### Part of

* **1** or more [word form]
* **1** [head]


part of speech
==============
[part of speech]: #part-of-speech

> ⚠️  **Deprecated** — use [specific word class][] instead.

The grammatical category to which a [term][] belongs.
Different parts of speech have different functions in a
[clause][].

Part of
-------

-   **1** or more [word class][]
-   **1** [term][]

phrase
======
[phrase]: #phrase

Multiple [word forms][] that, together, have one [meaning][].
A [dictionary entry][] may use a phrase as a [head][].

Is composed of
--------------

-   **2 or more** [word forms][]

Can be a
--------

-   **1** [head][]


user query
==========
[user query]: #user-query


_also **query**, **search string**_.

How the user writes their _search intent_, as a series of Unicode code
points. This might be a messy, misspelled, strangely written string.
It is the job of the intelligent dictionary to take this wild thing
and make sense of it, returning results that satisfy the user's search
intent.


word class
==========
[word class]: #word-class
[word classes]: #word-class
[specific word class]: #word-class

> Also known as **specific word class**

Category of \$THING that [inflects][] in a similar way. Members of the
same word class behave morphologically in a similar way to each other.

Contains
--------

-   **1 or more** [inflectional categories][].

in Plains Cree
--------------

These are the word classes in Plains Cree:

-   [NA][]
-   [NI][]
-   [NAD][]
-   [NID][]
-   [VII][]
-   [VAI][]
-   [VTI][]
-   [VTA][]
-   [Ipc][] --- [indeclinable particle][]
