/**
 * Shared crkeng + cwdeng toimportjson script.
 *
 * Turns ndjson to importjson.
 */

import { readFile } from "fs/promises";
import { join as joinPath } from "path";
import { Command } from "commander";
import { execIfMain } from "execifmain";
import { intersection, isEqual, min, uniqBy } from "lodash";
import { Transducer } from "hfstol";
import { resourceDir } from "../shared/util";
import { Analysis } from "../shared/dictionary";
import { CrkImport, CwdImport } from "./import";

export type NdjsonEntry = {
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

export type CreeLinguistInfo = {
  pos?: string;
  inflectional_category?: string;
  stem?: string;
  proto_cree?: string;
};

const CRK_RESOURCE_DIR = resourceDir("crkeng");
const CRK_DICTIONARY_DIR = joinPath(CRK_RESOURCE_DIR, "dictionary");
const CRK_FST_DIR = joinPath(CRK_RESOURCE_DIR, "fst");

const CWD_RESOURCE_DIR = resourceDir("cwdeng");
const CWD_DICTIONARY_DIR = joinPath(CWD_RESOURCE_DIR, "dictionary");

export const PERSONAL_PRONOUNS = new Set([
  // Personal pronouns
  "niýa",
  "kiýa",
  "wiýa",
  "niýanân",
  "kiýânaw",
  "kiýawâw",
  "wiýawâw",
]);

export const DEMONSTRATIVE_PRONOUNS = new Set([
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
const TIE_BREAKERS = [
  ["maskwa+N+A+Sg", "maskwa+N+A+Obv"],
  ["niska+N+A+Sg", "niska+N+A+Obv"],
  ["môswa+N+A+Sg", "môswa+N+A+Obv"],
];

// A list of tags which indicate different lexemes, e.g., nêwokâtêw+N vs
// nêwokâtêw+V+II, as opposed to tags like +Sg/+Pl that indicate different
// wordforms in the same lexeme.
//
// Used by the Dictionary class to link up wordforms into lexemes.
export const CREE_LEXICAL_TAGS = [
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

function getTieBreaker(analyses: Analysis[]) {
  // FIXME: on all but tiny input dictionaries, tieBreakers should be turned
  // into a map by lemma.
  const smushed = analyses.map((a) => smushAnalysis(a));
  for (const tb of TIE_BREAKERS) {
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

let analyzer: Transducer;

export function smushAnalysis(lemma_with_affixes: Analysis) {
  const [prefixTags, lemma, suffixTags] = lemma_with_affixes;
  return [prefixTags.join(""), lemma, suffixTags.join("")].join("");
}

/**
 * Attempt to infer the correct FST analysis of the provided head, given the pos.
 *
 * matchAnalysis() does the work of figuring out if an FST analysis could
 * potentially apply to the given headword. If there are multiple viable
 * candidates, this method tries to pick the best one.
 *
 * Currently it will pick the matching analysis with the lowest tag count if
 * there is one, otherwise it requires a manual entry in TIE_BREAKERS
 * above.
 *
 * `key` is only used for error/warning messages.
 */
export function inferAnalysis({
  head,
  protoHead,
  pos,
  key,
}: {
  head: string;
  protoHead: string;
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
    const match = matchAnalysis(a, { head, pos, protoHead });
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

/**
 * If the FST analysis matches, return {analysis, paradigm}. Otherwise return null.
 *
 * For example, a +V+II analysis will match to an entry with pos = VII, but
 * not to one with pos = VAI.
 */
export function matchAnalysis(
  analysis: Analysis,
  { head, pos, protoHead }: { head: string; pos: unknown; protoHead: string }
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
    PERSONAL_PRONOUNS.has(protoHead) &&
    suffixTags.includes("+Pron") &&
    suffixTags.includes("+Pers")
  ) {
    return { analysis, paradigm: "personal-pronouns" };
  }

  if (
    pos === "PrA" &&
    DEMONSTRATIVE_PRONOUNS.has(protoHead) &&
    suffixTags.includes("+Pron") &&
    suffixTags.includes("+Dem") &&
    suffixTags.includes("+A")
  ) {
    return { analysis, paradigm: "demonstrative-pronouns" };
  }

  if (
    pos === "PrI" &&
    DEMONSTRATIVE_PRONOUNS.has(protoHead) &&
    suffixTags.includes("+Pron") &&
    suffixTags.includes("+Dem") &&
    suffixTags.includes("+I")
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

  const lexicalDatabase = await readFile(options.inputNdjson, "utf8");

  const imports = [
    new CrkImport(options.outputCrkengFile),
    new CwdImport(options.outputCwdengFile),
  ];

  for (const piece of lexicalDatabase.split("\n")) {
    if (!piece.trim()) {
      continue;
    }

    const obj = JSON.parse(piece) as NdjsonEntry;
    for (const imp of imports) {
      imp.processEntry(obj);
    }
  }

  for (const imp of imports) {
    await imp.save({ pretty: options.prettier });
  }
}

execIfMain(main);
