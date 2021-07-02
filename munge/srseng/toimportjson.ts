import { execIfMain } from "execifmain";
import { writeFile } from "fs/promises";
import { Command } from "commander";
import { join as joinPath, resolve as resolvePath } from "path";
import { loadTsvFile } from "./util";
import { Dictionary } from "./dictionary";
import { Transducer } from "hfstol";

const RESOURCE_DIR = resolvePath(
  __dirname,
  "..",
  "..",
  "src",
  "srseng",
  "resources"
);

const DICTIONARY_DIR = joinPath(RESOURCE_DIR, "dictionary");
const FST_DIR = joinPath(RESOURCE_DIR, "fst");

const relaxedAnalyzer = new Transducer(
  joinPath(FST_DIR, "analyser-gt-desc.hfstol")
);

// TODO: the FST should recognize these forms directly, even if only in relaxed
// mode.
function headwordToFstLemma(headword: string) {
  return (
    headword
      .replace(/[ā]/g, "a")
      .replace(/[ī]/g, "i")
      .replace(/[ū]/g, "u")
      .replace(/[ō]/g, "o")
      // I'm not even sure these are equivalent; the FST yaml tests have both
      .replace(/[ʔ]/g, "'")
  );
}

async function main() {
  const program = new Command();
  program
    .option(
      "--input-tsv <file>",
      "The original source dictionary to use, in TSV format",
      `${DICTIONARY_DIR}/Onespot-Sapir - Vocabulary list - OS-Vocabulary.tsv`
    )
    .option(
      "--output-file <file>",
      "Where to write the generated importjson file",
      `${DICTIONARY_DIR}/srseng_dictionary.importjson`
    );

  program.parse();

  const options = program.opts();

  const inputTsv = await loadTsvFile(options.inputTsv);
  const dictionary = new Dictionary();
  let previousHead = "";

  for (const row of inputTsv) {
    let head = row["Bruce - Tsuut'ina text"];
    if (!head && !previousHead) {
      continue;
    }
    if (!head) {
      head = previousHead;
    }

    // FIXME HACK: update source dictionary instead!
    if (head === "gūyīsʔín" || head === "gīmīyīsʔín") {
      // difference, FST vs. dictionary
      head = head.replace(/n$/, "");
    }

    const entry = dictionary.getOrCreate(head);
    entry.addDefinition(row["Bruce - English text"]);

    const analyses = relaxedAnalyzer.lookup_lemma_with_affixes(
      headwordToFstLemma(head)
    );
    if (analyses.length > 1) {
      console.log(`Multiple analyses for ${head}; ${JSON.stringify(analyses)}`);
    } else if (analyses.length === 1) {
      let [_prefixTags, lemma, suffixTags] = analyses[0];
      entry.analysis = analyses[0];
      // TODO: some day, head words and FST lemmas will be distinct
      entry.head = lemma;

      if (suffixTags.includes("+V") && suffixTags.includes("+I")) {
        entry.paradigm = "VI";
      } else if (suffixTags.includes("+V") && suffixTags.includes("+T")) {
        entry.paradigm = "VT";
      } else if (suffixTags.includes("+V") && suffixTags.includes("+D")) {
        entry.paradigm = "VD";
      }
    }

    previousHead = head;
  }

  await writeFile(options.outputFile, dictionary.toJson());
}

execIfMain(main);
