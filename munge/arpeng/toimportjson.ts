import { resourceDir } from "../shared/util";
import { Command } from "commander";
import { Dictionary } from "../shared/dictionary";
import { intersection } from "lodash";

const { Transducer } = require("hfstol");
const { execIfMain } = require("execifmain");
const { readFile, writeFile } = require("fs/promises");
const { join: joinPath } = require("path");

const RESOURCE_DIR = resourceDir("arpeng");
const DICTIONARY_DIR = joinPath(RESOURCE_DIR, "dictionary");
const FST_DIR = joinPath(RESOURCE_DIR, "fst");

type ArapahoLexiconEntry = {
  base_form: string;
  status: string;
  pos: string;
  lex: string;
  senses: [{ definition: string }];
  // Only used to populate linguistInfo:
  morphology: string;
};
type AraphoLexicon = { [id: string]: ArapahoLexiconEntry };

type AraphoLinguistInfo = {
  sourceIds?: string[];
  pos?: string;
  morphologies?: string[];
};

/**
 * Entries from arapho_lexicon.json to skip. Entries are identified by key, but
 * only skipped if all of the indicated properties match: that way, if the
 * source entry is updated to no longer be problematic, it will no longer be
 * automatically excluded.
 */
const ENTRIES_TO_SKIP = new Map<string, Partial<ArapahoLexiconEntry>>([
  ["L3", { base_form: "'" }],
]);

async function main() {
  const program = new Command();
  program
    .option(
      "--input-lexicon <file>",
      "The original source dictionary to use",
      `${DICTIONARY_DIR}/arapaho_lexicon.json`
    )
    .option(
      "--output-file <file>",
      "Where to write the generated importjson file",
      `${DICTIONARY_DIR}/arpeng_dictionary.importjson`
    );

  program.parse();

  const options = program.opts();

  const normativeAnalyzer = new Transducer(
    joinPath(FST_DIR, "analyser-gt-norm.hfstol")
  );
  const normativeGenerator = new Transducer(
    joinPath(FST_DIR, "generator-gt-norm.hfstol")
  );
  const descriptiveAnalyzer = new Transducer(
    joinPath(FST_DIR, "analyser-gt-desc.hfstol")
  );

  const lexicalDatabase = JSON.parse(
    await readFile(options.inputLexicon, "utf-8")
  ) as AraphoLexicon;

  const dictionary = new Dictionary<AraphoLinguistInfo>([]);

  for (const [key, obj] of Object.entries(lexicalDatabase)) {
    if (obj.status === "deleted") {
      continue;
    }

    const head = obj.base_form;
    if (!head) {
      continue;
    }

    // Skip certain entries listed with matching key, but only if specified
    // properties still match
    let exclusion = ENTRIES_TO_SKIP.get(key);
    if (exclusion) {
      let shouldExclude = true;
      let propertyName: keyof ArapahoLexiconEntry;
      for (propertyName in exclusion) {
        if (exclusion[propertyName] !== obj[propertyName]) {
          shouldExclude = false;
          break;
        }
      }
      if (shouldExclude) {
        continue;
      }
    }

    const entry = dictionary.getOrCreate({ text: head });
    // The new ??= local assignment operator would need NodeJS 16
    entry.linguistInfo = entry.linguistInfo ?? {};
    if (entry.linguistInfo.pos && entry.linguistInfo.pos !== obj.pos) {
      console.log(
        `Warning: pos mismatch: ${JSON.stringify(entry.linguistInfo)} ${
          entry.head
        } ${entry.paradigm} vs ${key} ${head} ${obj.pos}`
      );
    }
    entry.linguistInfo.pos = obj.pos;

    entry.linguistInfo.sourceIds = entry.linguistInfo?.sourceIds ?? [];
    entry.linguistInfo.sourceIds.push(key);

    entry.linguistInfo.morphologies = entry.linguistInfo?.morphologies ?? [];
    if (
      obj.morphology &&
      !entry.linguistInfo.morphologies.includes(obj.morphology)
    ) {
      entry.linguistInfo.morphologies.push(obj.morphology);
    }

    for (const sense of obj.senses) {
      const { definition } = sense;
      if (definition) {
        entry.addDefinition(definition, ["ALD"]);
      }
    }

    // TODO: could also use obj.pos, e.g., `vii`, to disambiguate when there are
    // multiple analyses
    const normativeAnalyses = normativeAnalyzer.lookup_lemma_with_affixes(head);
    if (normativeAnalyses.length === 1) {
      entry.analysis = normativeAnalyses[0];
    } else if (normativeAnalyses.length > 1) {
      console.log(`multiple normative analyses for ${head}`);
    } else {
      const descriptiveAnalyses = descriptiveAnalyzer.lookup_lemma_with_affixes(
        head
      );
      if (descriptiveAnalyses.length === 1) {
        entry.analysis = descriptiveAnalyses[0];
      } else if (descriptiveAnalyses.length > 1) {
        console.log(`multiple descriptive analyses for ${head}`);
      } else {
        // could warn here, not analyzable
      }
    }

    // Now, assign paradigms. There are more paradigms but this is the only one
    // we have a paradigm table for right now.
    for (const paradigm of ["AI", "II", "TA", "TI"]) {
      if (
        entry.analysis &&
        intersection(entry.analysis[0], ["[VERB]", `[${paradigm}]`]).length ===
          2
      ) {
        entry.paradigm = paradigm;
        break;
      }
    }

    // If analyzing the base form didn’t work, try using the lex field as an FST
    // lemma
    if (!entry.analysis && normativeAnalyses.length === 0) {
      for (const [pos, paradigm, template] of [
        [
          "vti",
          "TI",
          (lemma) =>
            `[VERB][TI][INANIMATE-OBJECT][AFFIRMATIVE][PRESENT][IC]${lemma}[3SG-SUBJ]`,
        ],
        [
          "vai",
          "AI",
          (lemma) =>
            `[VERB][AI][ANIMATE-SUBJECT][AFFIRMATIVE][PRESENT][IC]${lemma}[1SG-SUBJ]`,
        ],
        [
          "vii",
          "II",
          (lemma) =>
            `[VERB][II][INANIMATE-SUBJECT][AFFIRMATIVE][PRESENT][IC]${lemma}[3SG-SUBJ]`,
        ],
        [
          "vta",
          "TA",
          (lemma) =>
            `[VERB][TA][ANIMATE-OBJECT][AFFIRMATIVE][PRESENT][IC]${lemma}[1SG-SUBJ][2SG-OBJ]`,
        ],
      ] as [string, string, (lemma: string) => string][]) {
        if (obj.pos.startsWith(pos)) {
          const lemma = obj.lex.replace(/-$/, "");
          const generated = normativeGenerator.lookup(template(lemma));
          if (generated.length !== 0) {
            entry.fstLemma = lemma;
            entry.paradigm = paradigm;
            break;
          }
        }
      }
    }
  }

  await writeFile(options.outputFile, dictionary.assemble());
  console.log(`Wrote ${options.outputFile}`);
}

execIfMain(main, module);
