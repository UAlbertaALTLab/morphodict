import { makePrettierJson } from "./util";
import assert from "assert";

type Analysis = [string[], string, string[]];

class DictionaryEntry {
  head?: string;
  analysis?: Analysis;
  paradigm?: string;
  senses?: { definition: string; sources: string[] }[];
  slug?: string;

  addDefinition(definition: string) {
    if (!definition.trim()) {
      return;
    }

    if (this.senses === undefined) {
      this.senses = [];
    }
    for (const k of this.senses) {
      if (k.definition === definition) {
        return;
      }
    }
    this.senses.push({ definition, sources: ["OS"] });
  }
}

export class Dictionary {
  _entries: DictionaryEntry[];
  _byText: Map<string, DictionaryEntry>;

  constructor() {
    this._entries = [];
    this._byText = new Map();
  }

  // This is a quick-and-dirty version; the git history has a slug_disambiguator
  // function with a fairly general-purpose algorithm that could be ported to
  // js.
  assignSlugs() {
    const used = new Set<string>();
    for (const e of this._entries) {
      if (e.slug) {
        assert(used.has(e.slug));
        used.add(e.slug);
      } else {
        let saferHeadWord = e.head!.replace(/[/\\ ]+/g, "_");

        let newSlug;
        if (!used.has(saferHeadWord)) {
          newSlug = saferHeadWord;
        } else {
          for (let i = 1; ; i++) {
            let proposed = `${saferHeadWord}.${i}`;
            if (!used.has(proposed)) {
              newSlug = proposed;
              break;
            }
          }
        }
        used.add(newSlug!);
        e.slug = newSlug;
      }
    }
  }

  getOrCreate(text: string) {
    assert(text);

    let existing = this._byText.get(text);
    if (existing) {
      return existing;
    }

    const entry = new DictionaryEntry();
    entry.head = text;
    this._entries.push(entry);
    this._byText.set(text, entry);
    return entry;
  }

  toJson() {
    this.assignSlugs();

    const entriesToExport = [];
    for (const e of this._entries) {
      if (!e.senses || e.senses.length === 0) {
        console.log(`Warning: no definitions for ${JSON.stringify(e)}`);
      } else {
        entriesToExport.push(e);
      }
    }
    return makePrettierJson(entriesToExport);
  }
}
