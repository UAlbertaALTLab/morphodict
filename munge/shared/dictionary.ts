import assert from "assert";
import {groupBy, minBy, remove, sortBy, union} from "lodash";
import jsonStableStringify from "json-stable-stringify";
import {DefaultMap, makePrettierJson, stringDistance, zip} from "./util";
import {disambiguateSlugs} from "./slug-disambiguator";

export type Analysis = [string[], string, string[]];
type DefinitionList = {
  definition: string;
  sources: string[];
}[];

type DefaultLinguistInfo = never;

export class DictionaryEntry<L> {
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

export class Wordform<L> {
  head?: string;
  analysis?: Analysis;
  senses?: DefinitionList;
  formOf?: DictionaryEntry<L>;
}

type ExportableWordform<L> = Required<Omit<Wordform<L>, "formOf">> & {
  formOf: string;
};

type NonFunctionMembers<T> = {
  [key in keyof T]: T[key] extends Function ? never : T[key];
};

/**
 * A non-class version of DictionaryEntry, to represent the JSON-serialized form.
 */
interface ExportableDictionaryEntry<L>
  extends NonFunctionMembers<DictionaryEntry<L>> {}

export type ImportJsonJsonEntry<L> =
  | ExportableDictionaryEntry<L>
  | ExportableWordform<L>;

export class Dictionary<L = DefaultLinguistInfo> {
  /**
   * FST tags which distinguish the lexeme, e.g., +N and +V, as opposed to tags
   * that distinguish the wordform within a lexeme, e.g., +Sg and +Pl.
   */
  readonly _lexicalTags: Set<string> | null;
  _entries: (DictionaryEntry<L> | Wordform<L>)[];
  /* WARNING: only holds DictionaryEntry object, not Wordforms */
  _byText: Map<string, DictionaryEntry<L>[]>;
  _bySlug: Map<string, DictionaryEntry<L>>;

  constructor(lexicalTags?: string[]) {
    if (lexicalTags) {
      this._lexicalTags = new Set(lexicalTags);
    } else {
      this._lexicalTags = null;
    }
    this._entries = [];
    this._byText = new Map();
    this._bySlug = new Map();
    this._bySlug = new Map();
  }

  /**
   * Create a new Dictionary object from pre-existing importjson-format data.
   */
  static fromJson<L>(jsonText: string): Dictionary<L> {
    const dictionary = new Dictionary<L>();

    const data = JSON.parse(jsonText) as ImportJsonJsonEntry<L>[];
    const forms = [];
    for (const d of data) {
      if ("formOf" in d) {
        forms.push(d);
      } else {
        const entry = dictionary.getOrCreate({ text: d.head!, slug: d.slug });
        entry.analysis = d.analysis;
        entry.paradigm = d.paradigm;
        entry.senses = d.senses;
        entry.slug = d.slug;
      }
    }

    return dictionary;
  }

  assignSlugs(keyfunc = (entry: DictionaryEntry<L>) => "") {
    function saferHeadWordForSlug(head: string) {
      return head.replace(/[/\\ ]+/g, "_");
    }

    const wordsNeedingSlugs = groupBy(
      this._entries.filter(
        (e) => e instanceof DictionaryEntry && !e.slug
      ) as DictionaryEntry<L>[],
      (e) => saferHeadWordForSlug(e.head!)
    );

    for (const [baseSlug, entries] of Object.entries(wordsNeedingSlugs)) {
      const disambiguators = disambiguateSlugs(entries.map((e) => keyfunc(e)));
      for (const [entry, disambiguator] of zip(entries, disambiguators)) {
        let slug = `${baseSlug}${disambiguator}`;
        if (this._bySlug.has(slug)) {
          throw new Error(`Attempted to reuse slug ${slug}`);
        }
        entry.slug = slug;
        this._bySlug.set(slug, entry);
      }
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
        byFstLemmaAndLexicalTags.getOrCreate(key).push(e);
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

    const entry = this.create(text);
    if (slug) {
      entry.slug = slug;
      this._bySlug.set(slug, entry);
    }

    return entry;
  }

  /**
   * Create a new entry. Useful for creating homographs.
   */
  create(text: string) {
    assert(text);

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

    this._entries.push(entry);

    return entry;
  }

  addWordform(form: Wordform<L>) {
    assert(form instanceof Wordform);
    this._entries.push(form);
  }

  /**
   * Remove an entry, and all linked wordforms, from the dictionary.
   */
  remove(entry: DictionaryEntry<L> | Wordform<L>) {
    remove(this._entries, (e) => e === entry);

    if (entry instanceof DictionaryEntry) {
      remove(this._byText.get(entry.head!)!, (e) => e === entry);
      if (entry.slug) {
        this._bySlug.delete(entry.slug);
      }
      const formsToRemove = this._entries.filter(
        (e) => e instanceof Wordform && e.formOf === entry
      );
      for (const f of formsToRemove) {
        this.remove(f);
      }
    }
  }

  /**
   * Assign slugs, determine lemmas, and return a prettified JSON string for the
   * dictionary as a whole.
   */
  assemble({ pretty } = { pretty: true }) {
    this.assignSlugs();
    this.determineLemmas();

    let entriesToExport: ImportJsonJsonEntry<L>[] = [];
    for (const e of this._entries) {
      if (!e.senses || e.senses.length === 0) {
        console.log(`Warning: no definitions for ${JSON.stringify(e)}`);
        continue;
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
        entriesToExport.push(e as ExportableDictionaryEntry<L>);
      }
    }

    entriesToExport = sortBy(entriesToExport, entryKeyBySlugThenText);

    if (pretty) {
      return makePrettierJson(entriesToExport);
    } else {
      return jsonStableStringify(entriesToExport, { space: 2 });
    }
  }

  get lexicalTags() {
    if (!this._lexicalTags) {
      throw new Error(
        "Attempted to use lexical tags on dictionary not configured with any"
      );
    }
    return this._lexicalTags;
  }

  [Symbol.iterator]() {
    return this._entries[Symbol.iterator]();
  }
}

// If you change how this sort works, you should change the matching
// entry_sort_key function written in Python as well.
function entryKeyBySlugThenText<T>(entry: ImportJsonJsonEntry<T>) {
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
