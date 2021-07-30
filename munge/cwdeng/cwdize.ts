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

class NdjsonDatabase {
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

function transliterateHeads(
  importjson: Dictionary<CreeLinguistInfo>,
  ndjson: NdjsonDatabase
) {
  const statCounts = new Counter();

  for (const entry of importjson) {
    const head = entry.head!;
    let proto = head;

    statCounts.increment("entries");

    // Don’t bother doing the work of trying to find a proto version unless the
    // headword contains an ambiguous character. Not so much to save time as to
    // avoid a misleadingly large number of entries for which a unique ndjson
    // entry could not be found.
    if (/y/.test(head)) {
      statCounts.increment("entries with y");

      const matches = ndjson.getMatches(head);
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

    entry.head = protoToWoods(proto);
    if (entry instanceof DictionaryEntry && proto !== head) {
      if (entry.linguistInfo == undefined) {
        entry.linguistInfo = {};
      }
      entry.linguistInfo!.proto = proto;
    }
  }
  console.log(statCounts);
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

  removeMdOnlyEntries(importjson);
  transliterateHeads(importjson, ndjson);

  await writeFile(options.outputImportjson, importjson.assemble());
}

execIfMain(main, module);
