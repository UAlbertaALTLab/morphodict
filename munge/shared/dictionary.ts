import assert from "assert";
import { minBy, sortBy, union } from "lodash";
import { DefaultMap, makePrettierJson, stringDistance } from "./util";

export type Analysis = [string[], string, string[]];
type DefinitionList = {
  definition: string;
  sources: string[];
}[];

type DefaultLinguistInfo = never;

class DictionaryEntry<L> {
  head?: string;
  analysis?: Analysis;
  paradigm?: string;
  senses?: DefinitionList;
  slug?: string;
  fstLemma?: string;
  linguistInfo?: L;

  addDefinition(definition: string, sources: string[]) {
    if (!definition.trim()) {
      return;
    }

    if (this.senses === undefined) {
      this.senses = [];
    }
    for (const k of this.senses) {
      if (k.definition === definition) {
        k.sources = union(k.sources, sources);
        return;
      }
    }
    this.senses.push({ definition, sources: sources.slice() });
  }
}

class Wordform<L> {
  head?: string;
  analysis?: Analysis;
  senses?: DefinitionList;
  formOf?: DictionaryEntry<L>;
}

type ExportableWordform<L> = Required<Omit<Wordform<L>, "formOf">> & {
  formOf: string;
};

export class Dictionary<L = DefaultLinguistInfo> {
  /**
   * FST tags which distinguish the lexeme, e.g., +N and +V, as opposed to tags
   * that distinguish the wordform within a lexeme, e.g., +Sg and +Pl.
   */
  readonly lexicalTags: Set<string>;
  _entries: (DictionaryEntry<L> | Wordform<L>)[];
  _byText: Map<string, DictionaryEntry<L>[]>;
  _bySlug: Map<string, DictionaryEntry<L>>;

  constructor(lexicalTags: string[]) {
    this.lexicalTags = new Set(lexicalTags);
    this._entries = [];
    this._byText = new Map();
    this._bySlug = new Map();
  }

  // This is a quick-and-dirty version; the git history has a slug_disambiguator
  // function with a fairly general-purpose algorithm that could be ported to
  // js.
  assignSlugs() {
    for (const e of this._entries) {
      if (!(e instanceof DictionaryEntry)) {
        continue;
      }

      // Current algorithm to assign slugs doesn’t support importing entries
      // with existing slugs.
      if (e.slug) {
        continue;
      }

      let saferHeadWord = e.head!.replace(/[/\\ ]+/g, "_");

      let newSlug;
      if (!this._bySlug.has(saferHeadWord)) {
        newSlug = saferHeadWord;
      } else {
        for (let i = 1; ; i++) {
          let proposed = `${saferHeadWord}@${i}`;
          if (!this._bySlug.has(proposed)) {
            newSlug = proposed;
            break;
          }
        }
      }
      this._bySlug.set(newSlug!, e);
      e.slug = newSlug;
    }
  }

  /**
   * Group entries by FST lemma, elect one entry to be the lemma, and demote the
   * rest to wordforms.
   */
  determineLemmas() {
    // Save locations for replacing with Wordform objects
    const entryIndices = new Map<DictionaryEntry<L>, number>();
    for (let i = 0; i < this._entries.length; i++) {
      const e = this._entries[i];
      if (e instanceof DictionaryEntry) {
        entryIndices.set(e, i);
      }
    }

    // Group by lemma and lexical tags
    const byFstLemmaAndLexicalTags = new DefaultMap<
      string,
      DictionaryEntry<L>[]
    >(() => Array());
    for (const e of this._entries) {
      if (e instanceof DictionaryEntry) {
        if (!e.analysis) {
          continue;
        }
        const fstLemma = e.fstLemma ?? e.analysis[1];
        const lexicalTags = this._extractLexicalTags(e.analysis);
        const key = JSON.stringify({ fstLemma, lexicalTags });
        byFstLemmaAndLexicalTags.get(key).push(e);
      }
    }

    // replace non-lemmas with wordform referring to lemmas
    for (const [key, entries] of byFstLemmaAndLexicalTags.entries()) {
      const { fstLemma } = JSON.parse(key);
      const lemmaEntry = minBy(entries, (e) =>
        stringDistance(fstLemma, e.head!)
      );
      assert(lemmaEntry);

      for (const e of entries) {
        if (e === lemmaEntry) {
          continue;
        }
        const wordform = new Wordform<L>();
        wordform.head = e.head;
        wordform.analysis = e.analysis;
        wordform.senses = e.senses;
        wordform.formOf = lemmaEntry;

        const index = entryIndices.get(e);
        assert(index);
        entryIndices.delete(e);
        this._entries[index] = wordform;
      }
    }
  }

  /**
   * Return the set of lexical tags, suitable for use as a lookup key.
   */
  private _extractLexicalTags(analysis: Analysis) {
    const tags = [...analysis[0], ...analysis[2]];
    const ret = [];
    for (const t of tags) {
      if (this.lexicalTags.has(t)) {
        ret.push(t);
      }
    }
    return [...new Set(ret)].sort();
  }

  getOrCreate({ text, slug }: { text: string; slug?: string }) {
    assert(text);

    if (slug) {
      const existing = this._bySlug.get(slug);
      if (existing) {
        assert(existing.head === text);
        return existing;
      }
    } else {
      const candidates = this._byText.get(text);
      // Passing different slugs may have created multiple entries with the same
      // text. In that case it’s an error to call getOrCreate and pass only text
      // and not a slug.
      assert(!candidates || candidates.length <= 1);
      if (candidates?.length === 1) {
        return candidates[0];
      }
    }

    const entry = new DictionaryEntry<L>();

    // This happens for a couple of entries in the Tsuut’ina “Vocabulary”
    // spreadsheet input.
    if (/^\p{Combining_Mark}/u.test(text.normalize())) {
      console.log(
        `Warning: ${JSON.stringify(text)} begins with a combining character`
      );
    }

    entry.head = text;
    let currentByTextList = this._byText.get(text);
    if (currentByTextList) {
      currentByTextList.push(entry);
    } else {
      this._byText.set(text, [entry]);
    }

    if (slug) {
      entry.slug = slug;
      this._bySlug.set(slug, entry);
    }

    this._entries.push(entry);

    return entry;
  }

  /**
   * Assign slugs, determine lemmas, and return a prettified JSON string for the
   * dictionary as a whole.
   */
  assemble({ pretty } = { pretty: true }) {
    this.assignSlugs();
    this.determineLemmas();

    let entriesToExport: (DictionaryEntry<L> | ExportableWordform<L>)[] = [];
    for (const e of this._entries) {
      if (!e.senses || e.senses.length === 0) {
        console.log(`Warning: no definitions for ${JSON.stringify(e)}`);
        continue;
      }
      if (e.head === "sa-") {
        debugger;
      }

      if (e instanceof Wordform) {
        const { head, analysis, senses } = e;
        assert(head);
        assert(analysis);
        const formOf = e.formOf!.slug;
        assert(formOf);
        entriesToExport.push({
          head,
          analysis,
          senses: senses ?? [],
          formOf,
        });
      } else {
        entriesToExport.push(e);
      }
    }

    entriesToExport = sortBy(entriesToExport, entryKeyBySlugThenText) as (
      | DictionaryEntry<L>
      | ExportableWordform<L>
    )[];

    if (pretty) {
      return makePrettierJson(entriesToExport);
    } else {
      return JSON.stringify(entriesToExport, null, 2);
    }
  }
}

// If you change how this sort works, you should change the matching
// entry_sort_key function written in Python as well.
function entryKeyBySlugThenText<T>(
  entry: DictionaryEntry<T> | ExportableWordform<T>
) {
  let slug: string;
  let form: string;

  if ("slug" in entry) {
    assert(entry.slug);
    slug = entry.slug;
    form = "";
  } else if ("formOf" in entry) {
    slug = entry.formOf;
    form = entry.head;
  } else {
    assert(false);
  }

  slug = slug!.normalize("NFD");
  form = form!.normalize("NFD");

  return [slug, form];
}
