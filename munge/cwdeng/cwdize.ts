/**
 * Script to create a cwdeng dictionary from crkeng importjson by:
 *   - removing MD definitions
 *   - getting proto head from ndjson and using to transliterate
 */

import { execIfMain } from "execifmain";
import { Command } from "commander";
import { join as joinPath } from "path";
import { Counter, DefaultMap, resourceDir } from "../shared/util";
import { Dictionary, DictionaryEntry } from "../shared/dictionary";
import { readFile, writeFile } from "fs/promises";
import { readNdjsonFile } from "./util";
import { every, remove } from "lodash";

export type NdjsonEntry = {
  dataSources: {
    [SourceAbbreviation: string]: {
      senses: { definition: string }[];
      pos?: string;
      stems?: string[];
    };
  };
  lemma?: { proto?: string; sro?: string };
};

const CRK_DICTIONARY_DIR = joinPath(resourceDir("crkeng"), "dictionary");
const CWD_DICTIONARY_DIR = joinPath(resourceDir("cwdeng"), "dictionary");

interface CreeLinguistInfo {
  inflectional_category?: string;
  pos?: string;
  stem?: string;
  wordclass?: string;
  proto?: string;
}

function protoToWoods(s: string) {
  let ret = s;
  ret = ret.replace(/ý/g, "th");
  ret = ret.replace(/ê/g, "î");
  return ret;
}

function toMacrons(s: string) {
  let ret = s;
  ret = ret.replace(/â/g, "ā");
  ret = ret.replace(/[êî]/g, "ī");
  ret = ret.replace(/ô/g, "ō");
  return ret;
}

export class NdjsonDatabase {
  private _entries;
  private _byHead;

  constructor(entries: NdjsonEntry[]) {
    this._entries = entries;
    this._byHead = new DefaultMap<string, NdjsonEntry[]>((k) => []);

    for (const e of this._entries) {
      if (!e.lemma) debugger;
      if (e.lemma?.sro) {
        this._byHead.getOrCreate(e.lemma.sro).push(e);
      }
    }
  }

  getMatches(head: string) {
    return this._byHead.get(head);
  }
}

// visible for testing
export function removeMdOnlyEntries(importjson: Dictionary<CreeLinguistInfo>) {
  const entriesToRemove = [];
  for (const entry of importjson) {
    const senses = entry.senses ?? [];
    for (const sense of senses) {
      remove(sense.sources, (source) => source === "MD");
    }
    remove(senses, (s) => s.sources.length === 0);

    if (senses.length === 0) {
      entriesToRemove.push(entry);
    }
  }
  // second loop to avoid mutating while iterating
  for (const entry of entriesToRemove) {
    importjson.remove(entry);
  }
}

function cleanupLinguistInfo(linguistInfo: CreeLinguistInfo) {
  const unsafeLinguistInfo = linguistInfo as { [key: string]: unknown };
  // Currently, these keys are not used by morphodict, but do exist in the
  // production importjson. Don’t propagate them.
  delete unsafeLinguistInfo.as_is;
  delete unsafeLinguistInfo.inflectional_category_linguistic;
  delete unsafeLinguistInfo.inflectional_category_plain_english;
  delete unsafeLinguistInfo.wordclass_emoji;
  delete unsafeLinguistInfo.smushedAnalysis;
}

function transliterateHeads(
  importjson: Dictionary<CreeLinguistInfo>,
  ndjson: NdjsonDatabase
) {
  const statCounts = new Counter();

  for (const entry of importjson) {
    const origHead = entry.head!;
    let proto = origHead;

    statCounts.increment("entries");

    // Don’t bother doing the work of trying to find a proto version unless the
    // headword contains an ambiguous character. Not so much to save time as to
    // avoid a misleadingly large number of entries for which a unique ndjson
    // entry could not be found.
    if (/y/.test(origHead)) {
      statCounts.increment("entries with y");

      const matches = ndjson.getMatches(origHead);
      const matchCount = matches?.length ?? 0;
      statCounts.increment(`${matchCount} matches`);

      if (matches) {
        const possibleProtos = matches.map((m) => m.lemma?.proto);

        if (
          possibleProtos[0] &&
          every(possibleProtos, (p) => p === possibleProtos[0])
        ) {
          proto = possibleProtos[0];
          statCounts.increment(`all protos match`);
        } else {
          // the algorithm here was going to be, if all matches have `y`s but no
          // `ý`s, or vice versa, transform `y`s in original head accordingly.
          // But with only 11 word(form)s hitting this case, it’s not worth
          // writing the code for that at the moment.
          statCounts.increment(`don’t know what to do`);
        }
      } else {
        statCounts.increment("no ndjson matches");
      }
    }

    if ("linguistInfo" in entry) {
      cleanupLinguistInfo(entry.linguistInfo ?? {});
    }

    entry.head = protoToWoods(proto);

    if (entry.head !== origHead) {
      // we’ve adjusted the headword; let’s adjust related fields too

      if (entry instanceof DictionaryEntry) {
        if (entry.analysis?.[1] === origHead) {
          entry.analysis![1] = protoToWoods(proto);
        }

        if (entry.linguistInfo == undefined) {
          entry.linguistInfo = {};
        }

        entry.linguistInfo!.proto = proto;

        let [baseSlug, suffix] = entry.slug!.split("@", 2);
        if (origHead === baseSlug) {
          entry.slug = protoToWoods(proto) + (suffix ? `@${suffix}` : "");
        }
        entry.slug = toMacrons(entry.slug!);
      }
    }
  }

  // now that all lemmas are adjusted, adjust non-lemma analyses
  for (const entry of importjson) {
    if (!("formOf" in entry)) {
      continue;
    }

    if (entry.analysis) {
      entry.analysis[1] = entry.formOf!.analysis![1];
    }
  }

  console.log("stats on matching crkeng entries to ndjson proto:");
  console.log(statCounts);
}

export function munge(
  importjson: Dictionary<CreeLinguistInfo>,
  ndjson: NdjsonDatabase
) {
  removeMdOnlyEntries(importjson);
  transliterateHeads(importjson, ndjson);
  return importjson.assemble({ lemmatize: false });
}

async function main() {
  const program = new Command();
  program
    .description("Interim script to build a cwdeng dictionary from crkeng one")
    .option(
      "--input-importjson <file>",
      "The production crkeng source dictionary to use, in importjson format",
      `${CRK_DICTIONARY_DIR}/crkeng_dictionary.importjson`
    )
    .option(
      "--input-ndjson <file>",
      "The DLX database to get proto-Cree forms from, in ndjson format",
      `${CRK_DICTIONARY_DIR}/database.ndjson`
    )
    .option(
      "--output-importjson <file>",
      "Where to write the generated importjson file",
      `${CWD_DICTIONARY_DIR}/cwdeng_dictionary.importjson`
    );

  program.parse();

  const options = program.opts();

  const ndjson = new NdjsonDatabase(await readNdjsonFile(options.inputNdjson));

  const importjson = Dictionary.fromJson<CreeLinguistInfo>(
    await readFile(options.inputImportjson, "utf8")
  );

  const assembled = munge(importjson, ndjson);
  await writeFile(options.outputImportjson, assembled);
  console.log(`Wrote ${options.outputImportjson}`);
}

execIfMain(main, module);
