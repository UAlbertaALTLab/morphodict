# Glossary

This is a glossary of terminology as used in the intelligent dictionary app.

- **This is not a glossary of linguistic terminology _per se_.** The definitions of terms in linguistics often vary from subfield to subfield, or depending on context. For the intelligent dictionary app, we need single, unambiguous definitions. Therefore this glossary focuses on how terms are operationalized and used in the intelligent dictionary app. The way terms are used in this app sometimes differ from how the terms are used in linguistics; these differences are noted where relevant.

  Many linguistics terms are however included in this glossary for informational purposes, even though the term might not be used in the app code.

- **This document is intended to be _normative_.** Code used by the app should align to the uses defined here.

## Contents

## Definitions

<dl>

  <dt id=affix>affix</dt>

  <dt id=analysis>analysis</dt>
  <dd>
    <p>(also: <dfn>linguistic analysis</dfn>; <dfn>linguistic breakdown</dfn>)</p>
    <p>An <em>ordered</em> list of the <a href=#lemma>lemma</a> and <a href=#feature>grammatical features</a> that describes an <a href=wordform>inflected wordform</a>. It minimally consists of:</p>
    <ul>
      <li>at least one <a href=#lemma>lemma</a></li>
      <li>at least one <a href=#feature>feature</a>, indicating the <a href=#wordform>wordform</a>'s <a href=#general-word-class>general word class</a>.</li>
    </ul>
    <h4>Example</h4>
    <p>A linguistic analysis for the Spanish word <i>sabía</i> is:</p>
    <pre><code>saber+V+Past+1Sg</code></pre>
    <p>This breakdown states:</p>
    <ul>
      <li>it's a form of the <a href=#lexeme>lexeme</a> <i>saber</i> <q>know</q> (where <i>saber</i> is the <a href=#lemma>lemma</a>)</li>
      <li>it's a verb (this is its <a href=#general-word-class>general word class</a>)</li>
      <li>it's past tense</li>
      <li>it has a <a href=#person>first person</a> <a href=#singular>singular</a> actor</li>
    </ul>
  </dd>

  <dt id=animacy>animacy</dt>

  <dt id=aspect>aspect</dt>

  <dt id=base>base</dt>

  <dt id=base-form>base form</dt>

  <dt id=bound>bound morpheme</dt>

  <dt id=citation-form>citation form</dt>
  <dd>
    <p>The form of the word used when the word is spoken in isolation. The intelligent dictionary is not directly concerned with citation forms, except in the incidental cases where the <a href=#lemma>lemma</a> happens to be a citation form.</p>
    <h4>Linguistic Notes</h4>
    <p>This is typically the form that a speaker gives when you ask, <q>How do you translate X?</q>, or the form represented by X in the question <q>What does X mean?</q>. Sometimes this varies: an English speaker might say <i>eat</i> or <i>to eat</i>. The <dfn>citation form</dfn> is not necessarily the same as the <a href=#head>head</a>, <a href=#lemma>lemma</a>, <a href=#minimal-word>minimal word</a>, or <a href=#stem>stem</a>, although it can be the any of these or other possibilities as well.<p>
    <h4>Examples</h4>
    <ul>
      <li><b>English</b>: The citation form for verbs in English is usually the infinitive. <i>to be</i> is the citation form of the verb <i>be</i>.</li>
      <li><b>Plains Cree:</b> The citation form for verbs is the third person singular independent (<small>3SG.INDEP</small>) form. <i>mîciw</i> is the citation form of the verb <i>mîci‑</i> <q>eat</q>.</li>
    </ul>
  </dd>

  <dt id=declension>declension</dt>
  <!-- also: declinable -->
  <!-- see also: conjugation; inflection -->

  <dt id=distributive>distributive</dt>
  <!-- see also: number, singular, dual, plural -->

  <dt id=dual>dual</dt>
  <!-- see also: number, singular, plural, distributive -->

  <dt id=entry>entry</dt>
  <!-- (dictionary) entry -->
  <!-- article, record -->

  <dt id=feature>feature</dt>
  <!-- (grammatical) feature -->
  <!-- morphosyntactic feature -->

  <dt id=free>free morpheme</dt>

  <dt id=functional-category>functional category</dt>

  <dt id=gender>gender</dt>
  <!-- semantic vs. grammatical gender -->
  <!-- see also: noun class -->

  <dt id=general-word-class>general word class</dt>

  <dt id=grammatical-category>grammatical category</dt>
  <!-- POS vs. grammatical feature -->

  <dt id=head>head(word|phrase|morpheme)</dt>
  <dd>
    <p>(also: <dfn>headword</dfn>; <dfn>head phrase</dfn>; <dfn>head morpheme</dfn>)</p>
    <p>The <dfn>head</dfn> of a <a href=#entry>dictionary entry</a> is the word under which a set of related definitions appears. In physical dictionaries, the <dfn>head</dfn> is used to alphabetize and look up dictionary entries. The term <dfn>headword</dfn> is sometimes used as a general cover term for headword, head phrase, and head morpheme, but the app code should use the more generic term <dfn>head</dfn> for this purpose instead.</p>
    <p>The head of a <a href=#entry>dictionary entry</a> is <em>usually</em> the <a href=#lemma>lemma</a>, but not always. Sometimes the headword requires capitalization or other orthographic changes. Simply put, the <dfn>head(word)</dfn> is the form of the lexeme the lexicographer wants the dictionary entry to be listed under.</p>
    <p><b>see also:</b> <a href=#lemma>lemma</a></p>
  </dd>

  <dt id=homograph>homograph</dt>
  <dd>
    <p>Two words are <dfn>homographs</dfn> if they are written the same way. Their pronounciations may or may not be the same. For example, <i>bow</i> <q>bend onself forward in respect</q> and <i>bow</i> <q>weapon for shooting arrows</q> are homographs but their pronounciations are different (/baʊ/ and /boʊ/ respectively).</p>
    <p><b>see also:</b> <a href=#homograph-number>homograph number</a>; <a href=#homonym>homonym</a></p>
  </dd>

  <dt id=homograph-number>homograph number</dt>
  <dd>
    <p>A <dfn>homograph number</dfn> is a number used to distinguish <a href=#homograph>homographs</a>. In dictionaries, it is common for this number to immediately follow the headword, sometimes in superscript or subscript. In the intelligent dictionary, homograph numbers are used on the backend to disambiguate <a href=#homograph>homographs</a>, but they are not displayed to the user.</p>
    <p><b>see also:</b> <a href=#homograph>homograph</a></p>
  </dd>

  <dt id=homonym>homonym</dt>

  <dt id=inflection>inflection</dt>
  <dd>
    <p>The parts of a word that indicate <a href=#grammatical-category>grammatical categories</a> such as <a href=#tense>tense</a>, <a href=#aspect>aspect</a>, <a href=#voice>voice</a>, <a href=#mood>mood</a>, <a href=#person>person</a>, <a href=#number>number</a>, <a href=#gender>gender</a>, <a href=#animacy>animacy</a>, etc.</p>
    <p>Sometimes <dfn>inflection</dfn> is also used to refer to the <a href=#conjugation>conjugation</a> paradigm of a verb or <a href=#declension>declension</a> paradigm of a noun.</p>
  </dd>

  <dt id=lemma>lemma</dt>
  <dd>
    <p>The <dfn>lemma</dfn> is the form of a <a href=#lexeme>lexeme</a> (or phrase or morpheme) conventionally used to represent that lexeme.</p>
    <p>The lemma may be any conventionally agreed-upon form of the word—the <a href=#citation-form>citation form</a>, the <a href=#stem>stem</a>, or a specific <a href=#wordform>inflected wordform</a>.</p>
    <p>It can be helpful to think of the lemma as the <em>label</em> for a lexeme.</p>
    <p>The <a href=#head>head</a> of a <a href=#entry>dictionary entry</a> is usually the lemma, but not always (see <a href=#head>head</a> for more details).</p>
    <p><b>Note:</b> The Plains Cree FST requires that the lemma be the citation form of the word.</p>
    <h4>Examples</h4>
    <ul>
      <li><b>English:</b> The lemma for the wordforms <i>am</i>, <i>are</i>, <i>is</i>, <i>was</i>, <i>were</i> is conventionally <i>be</i>.</li>
      <li><b>Plains Cree:</b> The lemma for the wordforms <i>nimîcin</i> <q>I eat</q>, <i>kimîcin</i> <q>you eat</q>, and <i>mîciw</i> <q>s/he eats</q> is <i>mîciw</i> <q>s/he eats</q>.</li>
    </ul>
    <section>
      <h4>References</h4>
      <blockquote cite='Svensén. 2009. A handbook of lexicography: The theory and practice of dictionary-making'>The lemma functions as a representative of a linguistic sign; in a dictionary it represents the lexical item described in the individual dictionary entry. (Svensén <a href=#Svensen2009>2009</a>: 93)</blockquote>
    </section>
    <p><b>see also:</b> <a href=#head>head</a></p>
  </dd>

  <dt id=lexeme>lexeme</dt>
  <dd>
    <p>A vocabulary item, or any item whose meaning must be memorized (a morpheme, a lexeme, or an idiomatic phrase). Lexemes often have many different <a href=#wordform>inflected wordforms</a> with different grammatical distinctions, but share a core semantic meaning. By convention, one of those forms is chosen to represent the lexeme, and that form is called the <dfn><a href=#lemma>lemma</a></dfn>.<p>
    <p>Sometimes the term <dfn>construction</dfn> is used as a more generic cover term for morpheme, lexeme, or idiomatic phrase.</p>
    <p><b>see also:</b> <a href=#lemma>lemma</a></p>
  </dd>

  <dt id=lexical>lexical</dt>
  <!-- TODO: as opposed to grammatical / functional -->

  <dt id=lexical-category>lexical category</dt>

  <dt id=lexicography>lexicography</dt>

  <dt id=paradigm>paradigm</dt>
  <!-- (inflectional) paradigm -->

  <dt id=prefix>prefix</dt>

  <dt id=minimal-word>minimal word</dt>

  <dt id=mood>mood</dt>

  <dt id=morpheme>morpheme</dt>

  <dt id=noun-class>noun class</dt>
  <!-- see also: gender -->

  <dt id=number>number</dt>
  <!-- semantic vs. grammatical number -->
  <!-- see also: singular, dual, plural, distributive -->

  <dt id=orthography>orthography</dt>

  <dt id=person>person</dt>
  <!-- semantic vs. grammatical person (e.g. royal 'we') -->

  <dt id=plural>plural</dt>
  <!-- see also: number, singular, dual, distributive -->

  <dt id=singular>singular</dt>
  <!-- see also: number, dual, plural, distributive -->

  <dt id=specific-word-class>specific word class</dt>

  <dt id=stem>stem</dt>
  <dd>
    <p>(also: <dfn>linguistic stem</dfn>; <dfn>lexical category</dfn>)</p>
    <p>The <dfn>stem</dfn> is the part(s) of the word which are common to all of its <a href=#wordform>inflected wordforms</a>. It is the part(s) of the word that <a href=#inflection>inflection</a> is added to.</p>
    <p>Stems may be continuous or discontinuous.</p>
    <!-- TODO: add examples of continuous vs. discontinuous -->
    <p>Stems are often <a href=#bound>bound forms</a> that always require additional affixes to be a complete word. When this is the case, stems are written with hyphens.</p>
  </dd>

  <dt id=suffix>suffix</dt>

  <dt id=tense>tense</dt>

  <dt id=voice>voice</dt>

  <dt id=word-class>word class</dt>
  <dd>
    <p>(also: <dfn>part of speech</dfn>)</p>
    <p>The term <dfn>word class</dfn> is ambiguous by itself and should be avoided. The app code should use the more precise terms <a href=#general-word-class>general word class</a> or <a href=#specific-word-class>specific word class</a> instead.<p>
    <p>In linguistics, <dfn>word class</dfn> is used to describe any division of words into categories or subcategories, such as Noun, Verb, Mass Noun, Demonstrative Pronoun, etc. Traditionally <dfn>word classes</dfn> were also called <dfn><a href=#part-of-speech>parts of speech</a></dfn>, although this term is becoming less common.</p>
    <p>The app code should avoid the term <a href=#part-of-speech>part of speech</a>.</p>
    <p>There are two types of word classes in linguistics: <dfn><a href=#lexical-category>lexical categories</a></dfn> that have concrete <a href=lexical>lexical</a> meanings, and <dfn><a href=#functional-category>functional categories</a></dfn> that have abstract grammatical meanings. Sometimes the term <dfn>lexical category</dfn> is used to refer more broadly to word classes.</p>
    <p>
      <b>see also:</b>
      <a href=#functional-category>functional category</a>;
      <a href=#general-word-class>general word class</a>;
      <a href=#lexical-category>lexical category</a>;
      <a href=#part-of-speech>part of speech</a>;
      <a href=#specific-word-class>specific word class</a>
    </p>
  </dd>

  <dt id=wordform>wordform</dt>
  <!-- (inflected) wordform -->

</dl>

## References

<ul>
  <li><p id=Svensen2009>Svensén, Bo. 2009. <cite>A handbook of lexicography: The theory and practice of dictionary-making.</cite> Cambridge University Press.</p></li>
</ul>

<!-- LINKS -->

[RFC-2119]: https://datatracker.ietf.org/doc/html/rfc2119
