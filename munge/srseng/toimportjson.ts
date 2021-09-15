import { join as joinPath } from "path";
import { writeFile } from "fs/promises";
import { difference, flatten, intersection, isEqual, min } from "lodash";
import { execIfMain } from "execifmain";
import { Command } from "commander";
import { Transducer } from "hfstol";
import { loadTsvFile, resourceDir } from "../shared/util";
import { Analysis, Dictionary } from "../shared/dictionary";

const RESOURCE_DIR = resourceDir("srseng");

const DICTIONARY_DIR = joinPath(RESOURCE_DIR, "dictionary");
const FST_DIR = joinPath(RESOURCE_DIR, "fst");

const analyzer = new Transducer(joinPath(FST_DIR, "analyser-gt-norm.hfstol"));

function tagCount(analysis: Analysis) {
  return analysis[0].length + analysis[2].length;
}

/**
 * Like Array.findIndex, except:
 *   - uses lodash isEqual, so can compare arrays and such
 *   - returns undefined if not found, or multiple matches exist
 */
function findEqualUniqueIndex<T>(array: T[], target: T) {
  let matchIndex = null;
  for (let i = 0; i < array.length; i++) {
    if (isEqual(array[i], target)) {
      if (matchIndex !== null) {
        // duplicate
        return null;
      }
      matchIndex = i;
    }
  }
  return matchIndex;
}

/**
 * If a single entry matches the tiebreaker rules, return it, otherwise return
 * null.
 */
function doTieBreaking(analyses: Analysis[]): Analysis | null {
  // Tsuut’ina-specific rules to break ties when there are multiple analyses

  const flattenedAnalyses = analyses.map(flatten);
  const commonTags = intersection(...flattenedAnalyses);
  const tags = flattenedAnalyses.map((e) => difference(e, commonTags));

  // Current rule: for each list of tags below, in order, try to see if there is
  // exactly one analysis that has all the same tags as the other analyses, plus
  // the ones given here. If so, choose it.
  //
  // XXX: Andrew put these in to try to get *something* working. A linguist
  // needs to replace them.
  for (const tieBreaker of [
    ["+Ipfv"],
    ["+DObjSg3"],
    ["+IObjSg3"],
    ["+SbjSg1", "+DObjSg3"],
    ["+SbjSg3"],
    ["+SbjSg1"],
  ]) {
    const index = findEqualUniqueIndex(tags, tieBreaker);
    if (index != null) {
      const ret = analyses[index];
      return ret;
    }
  }

  return null;
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

  const assembled = munge(inputTsv);
  await writeFile(options.outputFile, assembled);
}

export function munge(inputTsv: { [key: string]: string }[]) {
  const dictionary = new Dictionary(["+V", "+T", "+I", "+D"]);
  let previousHead = "";

  for (const row of inputTsv) {
    let head = row["Bruce - Tsuut'ina text"].normalize("NFC");
    if (!head && !previousHead) {
      continue;
    }
    if (!head) {
      head = previousHead;
    }

    const definition = row["Bruce - English text"];

    if (!definition) {
      console.log(`Warning: no definition for row with head ${head}`);
    }

    const entry = dictionary.getOrCreate({ text: head });
    entry.addDefinition(definition, ["OS"]);

    const analyses = analyzer.lookup_lemma_with_affixes(head);

    let analysis;
    if (analyses.length > 1) {
      // multiple analyses; start by taking minimum tag count
      const minTagCount = min(analyses.map((e) => tagCount(e)));
      const withMinTagCount = analyses.filter(
        (e) => tagCount(e) === minTagCount
      );
      if (withMinTagCount.length === 1) {
        analysis = withMinTagCount[0];
      } else {
        const tiebreaker = doTieBreaking(withMinTagCount);
        if (tiebreaker) {
          analysis = tiebreaker;
        } else {
          console.log(
            `Multiple analyses for ${head}; ${JSON.stringify(analyses)}`
          );
        }
      }
    } else if (analyses.length === 1) {
      analysis = analyses[0];
    }

    if (analysis) {
      let [_prefixTags, _lemma, suffixTags] = analysis;
      entry.analysis = analyses[0];

      if (suffixTags.includes("+V") && suffixTags.includes("+I")) {
        entry.paradigm = "VI";
      } else if (suffixTags.includes("+V") && suffixTags.includes("+T")) {
        entry.paradigm = "VT";
      } else if (suffixTags.includes("+V") && suffixTags.includes("+D")) {
        entry.paradigm = "VD";
      }
      // otherwise we don’t know what the paradigm is, so don’t set anything
      // here.
    }

    previousHead = head;
  }
  return dictionary.assemble();
}

execIfMain(main, module);
