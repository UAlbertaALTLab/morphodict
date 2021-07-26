"use strict";

/**
 * Shared crkeng + cwdeng toimportjson script.
 *
 * Turns ndjson to importjson.
 */

import { Command } from "commander";
import { resourceDir } from "../shared/util";
import { Analysis, Dictionary } from "../shared/dictionary";

const { Transducer } = require("hfstol");
const { execIfMain } = require("execifmain");
const { readFile, writeFile } = require("fs/promises");
const { join: joinPath } = require("path");
const { intersection, min, isEqual, uniqBy } = require("lodash");

type NdjsonEntry = {
  dataSources: {
    [SourceAbbreviation: string]: {
      senses: { definition: string }[];
      pos?: string;
      stm?: string;
      notes?: { noteType: string; text: string }[];
    };
  };
  lemma: { plains: string; sro?: string; md?: string };
  key: string;
};

type CreeLinguistInfo = {
  pos?: string;
  stem?: string;
  smushedAnalysis?: string;
  protoCree?: string;
};

const CRK_RESOURCE_DIR = resourceDir("crkeng");
const CRK_DICTIONARY_DIR = joinPath(CRK_RESOURCE_DIR, "dictionary");
const CRK_FST_DIR = joinPath(CRK_RESOURCE_DIR, "fst");

const CWD_RESOURCE_DIR = resourceDir("cwdeng");
const CWD_DICTIONARY_DIR = joinPath(CWD_RESOURCE_DIR, "dictionary");

const personalPronouns = new Set([
  // Personal pronouns
  "niya",
  "kiya",
  "wiya",
  "niyanân",
  "kiyânaw",
  "kiyawâw",
  "wiyawâw",
]);

const demonstrativePronouns = new Set([
  // Animate demonstratives
  "awa",
  "ana",
  "nâha",
  "ôki",
  "aniki",
  "nêki",
  // Inanimate demonstratives
  "ôma",
  "ôhi",
  "anima",
  "anihi",
  "nêma",
  "nêhi",
  // Inanimate/Obviative inanimate demonstratives
  "ôhi",
  "anihi",
  "nêhi",
]);

// If we’ve whittled choices down to just the analyses listed, take the first
// one in the list.
const tieBreakers = [
  ["maskwa+N+A+Sg", "maskwa+N+A+Obv"],
  ["niska+N+A+Sg", "niska+N+A+Obv"],
  ["môswa+N+A+Sg", "môswa+N+A+Obv"],
];

function getTieBreaker(analyses: Analysis[]) {
  // FIXME: on all but tiny input dictionaries, tieBreakers should be turned
  // into a map by lemma.
  const smushed = analyses.map((a) => smushAnalysis(a));
  for (const tb of tieBreakers) {
    if (isEqual(tb, smushed)) {
      for (const a of analyses) {
        if (smushAnalysis(a) === tb[0]) {
          return a;
        }
      }
    }
  }
  return null;
}

let analyzer: typeof Transducer;

/**
 * If the FST analysis matches, return {analysis, paradigm}. Otherwise return null.
 */
function matchAnalysis(
  analysis: Analysis,
  { head, pos }: { head: string; pos: unknown }
): { analysis: Analysis; paradigm: string | null } | null {
  if (!pos || !(typeof pos === "string")) {
    return null;
  }

  const [_prefixTags, _lemma, suffixTags] = analysis;

  if (pos.startsWith("I")) {
    if (suffixTags.includes("+Ipc")) {
      return { analysis, paradigm: null };
    }
  }

  if (
    pos === "PrA" &&
    personalPronouns.has(head) &&
    suffixTags.includes("+Pron") &&
    suffixTags.includes("+Pers")
  ) {
    return { analysis, paradigm: "personal-pronouns" };
  }

  if (
    (pos === "PrA" || pos === "PrI") &&
    demonstrativePronouns.has(head) &&
    suffixTags.includes("+Pron") &&
    suffixTags.includes("+Dem")
  ) {
    return { analysis, paradigm: "demonstrative-pronouns" };
  }

  if ((pos === "PrA" || pos === "PrI") && suffixTags.includes("+Pron")) {
    return { analysis, paradigm: null };
  }

  const specificWordClass = pos.split("-")[0];

  for (let [paradigmName, paradigmSpecificWordClass, paradigmTags] of [
    ["NA", "NA", ["+N", "+A"]],
    ["NI", "NI", ["+N", "+I"]],
    ["NDA", "NDA", ["+N", "+A", "+D"]],
    ["NDI", "NDI", ["+N", "+I", "+D"]],
    ["VTA", "VTA", ["+V", "+TA"]],
    ["VTI", "VTI", ["+V", "+TI"]],
    ["VAI", "VAI", ["+V", "+AI"]],
    ["VII", "VII", ["+V", "+II"]],
  ] as [string, string, string[]][]) {
    if (
      specificWordClass === paradigmSpecificWordClass &&
      intersection(paradigmTags, suffixTags).length === paradigmTags.length
    ) {
      return { analysis, paradigm: paradigmName };
    }
  }
  return null;
}

function smushAnalysis(lemma_with_affixes: Analysis) {
  const [prefixTags, lemma, suffixTags] = lemma_with_affixes;
  return [prefixTags.join(""), lemma, suffixTags.join("")].join("");
}

/**
 * `key` is only used for error/warning messages.
 */
function inferAnalysis({
  head,
  pos,
  key,
}: {
  head: string;
  pos?: string;
  key?: string;
}): { analysis?: Analysis; paradigm?: string; ok: boolean } {
  let ok = false;

  // bug? cwd analyzer has duplicate results for nitha
  const analyses = uniqBy(
    analyzer.lookup_lemma_with_affixes(head),
    smushAnalysis
  );
  // Does FST analysis match POS from toolbox file?
  let matches = [];
  for (const a of analyses) {
    const match = matchAnalysis(a, { head, pos });
    if (match) {
      matches.push(match);
    }
  }
  let analysis, paradigm;
  if (matches.length > 0) {
    // ôma analyzes as +Pron+Def or +Pron+Dem; since we have a paradigm for
    // the latter, let’s prefer it.
    const matchesWithParadigms = matches.filter((m) => m.paradigm !== null);
    if (matchesWithParadigms.length > 0) {
      matches = matchesWithParadigms;
    }

    function analysisTagCount(analysis: Analysis) {
      const [prefixTags, _lemma, suffixTags] = analysis;
      return prefixTags.length + suffixTags.length;
    }

    const minTagCount = min(matches.map((m) => analysisTagCount(m.analysis)));
    const matchesWithMinTagCount = matches.filter(
      (m) => analysisTagCount(m.analysis) === minTagCount
    );
    if (matchesWithMinTagCount.length === 1) {
      const bestMatch = matchesWithMinTagCount[0];
      analysis = bestMatch.analysis;
      paradigm = bestMatch.paradigm;
      ok = true;
    } else if (getTieBreaker(matchesWithMinTagCount.map((m) => m.analysis))) {
      const tieBreakerAnalysis = getTieBreaker(
        matchesWithMinTagCount.map((m) => m.analysis)
      );
      for (const m of matchesWithMinTagCount) {
        if (m.analysis === tieBreakerAnalysis) {
          analysis = m.analysis;
          paradigm = m.paradigm;
          ok = true;
          break;
        }
      }
      if (!ok) {
        throw Error("tie breaker exists but was not applied");
      }
    } else {
      console.log(`${matches.length} matches for ${key}`);
      ok = false;
    }
  } else {
    console.log(`${matches.length} matches for ${key}`);
    ok = false;
  }

  return { analysis, paradigm: paradigm ?? undefined, ok };
}

function protoToWoods(s: string) {
  let ret = s;
  ret = ret.replace(/ý/g, "th");
  ret = ret.replace(/ê/g, "î");
  return ret;
}

function protoToPlains(s: string) {
  let ret = s;
  ret = ret.replace(/ý/g, "y");
  return ret;
}

async function main() {
  const program = new Command();
  program
    .option(
      "--input-ndjson <file>",
      "The original source dictionary to use",
      `${CRK_DICTIONARY_DIR}/database.ndjson`
    )
    .option(
      "--output-crkeng-file <file>",
      "Where to write the generated importjson file",
      `${CRK_DICTIONARY_DIR}/crkeng_dictionary.importjson`
    )
    .option(
      "--output-cwdeng-file <file>",
      "Where to write the generated importjson file",
      `${CWD_DICTIONARY_DIR}/cwdeng_dictionary.importjson`
    )
    .option(
      "--no-prettier",
      `
        Skip running prettier. Saves time when debugging the code, but very
        strongly discouraged for files that may be distributed, as they are
        much harder to inspect when not run through prettier.`,
      false
    );

  program.parse();

  const options = program.opts();

  analyzer = new Transducer(
    `${CRK_FST_DIR}/crk-strict-analyzer-for-dictionary.hfstol`
  );

  // const transliterator = argv.woods ? protoToWoods : protoToPlains;

  const lexicalDatabase = await readFile(options.inputNdjson, "utf8");

  const CREE_LEXICAL_TAGS = [
    "+A",
    "+AI",
    "+D",
    "+I",
    "+II",
    "+N",
    "+TA",
    "+TI",
    "+V",
  ];

  const crkDictionary = new Dictionary<CreeLinguistInfo>(CREE_LEXICAL_TAGS);
  const cwdDictionary = new Dictionary<CreeLinguistInfo>(CREE_LEXICAL_TAGS);

  for (const piece of lexicalDatabase.split("\n")) {
    if (!piece.trim()) {
      continue;
    }

    const obj = JSON.parse(piece) as NdjsonEntry;

    const protoHead = obj.lemma.sro ?? obj.lemma.plains;

    for (const lang of ["crk", "cwd"] as const) {
      // For now, assume crk and cwd have same FSTs modulo orthography
      const crkHead = protoToPlains(protoHead);

      const head = lang === "crk" ? crkHead : protoToWoods(protoHead);

      if (!head) {
        continue;
      }

      // Skip MD-only entries for Woods Cree
      if (lang === "cwd" && isEqual(Object.keys(obj.dataSources), ["MD"])) {
        continue;
      }

      const entry = (lang === "crk"
        ? crkDictionary
        : cwdDictionary
      ).getOrCreate({ slug: obj.key, text: head });

      const pos = obj.dataSources?.CW?.pos;

      const isProbablyMorpheme =
        head.startsWith("-") || (head.endsWith("-") && pos !== "IPV");
      const shouldTryAssigningParadigm = !isProbablyMorpheme;

      const linguistInfo: CreeLinguistInfo = { pos };

      if (shouldTryAssigningParadigm) {
        let analysis;
        let paradigm;
        let ok = false;
        if (pos === "IPV") {
          ok = true;
        } else if (head.includes(" ")) {
          ok = true;
        } else {
          ({ analysis, paradigm, ok } = inferAnalysis({
            head: crkHead,
            pos,
            key: obj.key,
          }));
        }

        if (ok) {
          entry.analysis = analysis;
          entry.paradigm = paradigm;

          if (analysis) {
            linguistInfo.smushedAnalysis = smushAnalysis(analysis);
          }
        }
      }

      const stem = obj.dataSources?.CW?.stm;
      if (stem) {
        linguistInfo.stem = stem;
      }
      if (protoHead !== head) {
        linguistInfo.protoCree = protoHead;
      }
      entry.linguistInfo = linguistInfo;

      for (const sourceAbbrevation in obj.dataSources) {
        // No Maskwacîs entries for the Woods Cree dictionary.
        if (lang === "cwd" && sourceAbbrevation === "MD") {
          continue;
        }
        for (const sense of obj.dataSources[sourceAbbrevation].senses) {
          entry.addDefinition(sense.definition, [sourceAbbrevation]);
        }
      }

      // Until there is frontend support for notes, use notes as the definition
      // when there are no other definitions.
      if (
        (!entry.senses || entry.senses.length === 0) &&
        obj.dataSources.CW.notes
      ) {
        for (const note of obj.dataSources.CW.notes) {
          entry.addDefinition(`[${note.text}]`, ["CW"]);
        }
      }
    }
  }

  for (const [dict, file] of [
    [crkDictionary, options.outputCrkengFile],
    [cwdDictionary, options.outputCwdengFile],
  ] as const) {
    await writeFile(file, dict.assemble({ pretty: options.prettier }));
    console.log(`Wrote ${file}`);
  }
}

execIfMain(main);
