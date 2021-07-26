import { writeFile } from "fs/promises";

import { Dictionary } from "../shared/dictionary";
import {
  CREE_LEXICAL_TAGS,
  CreeLinguistInfo,
  DEMONSTRATIVE_PRONOUNS,
  inferAnalysis,
  NdjsonEntry,
  PERSONAL_PRONOUNS,
} from "./toimportjson";

import { isEqual } from "lodash";

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

function posFromInflectionalCategory(inflectionalCategory: string) {
  // this matches what the xml/CreeDictionary python code did;
  // it might be better to extract this from the tags

  if (inflectionalCategory.startsWith("N")) {
    return "N";
  }
  if (inflectionalCategory.startsWith("V")) {
    return "V";
  }
  if (inflectionalCategory === "INM") {
    return "N";
  }
  if (inflectionalCategory.startsWith("I")) {
    return "IPC";
  }
  if (inflectionalCategory.toUpperCase().startsWith("PR")) {
    return "PRON";
  }
  return "";
}

abstract class Import {
  _dictionary: Dictionary<CreeLinguistInfo>;
  _outputFileName: string;
  _unusedPersonalPronouns: Set<string>;
  _unusedDemonstrativePronouns: Set<string>;

  constructor(outputFileName: string) {
    this._dictionary = new Dictionary(CREE_LEXICAL_TAGS);
    this._outputFileName = outputFileName;

    this._unusedPersonalPronouns = new Set(PERSONAL_PRONOUNS);
    this._unusedDemonstrativePronouns = new Set(DEMONSTRATIVE_PRONOUNS);
  }

  processEntry(obj: NdjsonEntry) {
    const protoHead = obj.lemma.sro ?? obj.lemma.plains;

    // For now, assume crk and cwd have same FSTs modulo orthography
    const crkHead = protoToPlains(protoHead);

    const head = this.protoCreeToInternalOrthography(protoHead);

    if (!head) {
      return;
    }

    if (this.shouldSkipNdjsonEntry(obj)) {
      return;
    }

    // XXX: a few stem/morpheme(?) entries with keys like `/kotap-/`?
    let slug = obj.key.replace(/\//g, "_");
    slug = this.protoCreeToInternalOrthography(slug);
    const entry = this._dictionary.getOrCreate({
      slug: slug,
      text: head,
    });

    const pos = obj.dataSources?.CW?.pos?.toString();

    const isProbablyMorpheme =
      head.startsWith("-") || (head.endsWith("-") && pos !== "IPV");
    const shouldTryAssigningParadigm = !isProbablyMorpheme;

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
          protoHead,
          key: obj.key,
        }));
      }

      if (ok) {
        entry.analysis = analysis;
        entry.paradigm = paradigm;

        if (entry.paradigm === "demonstrative-pronouns") {
          this._unusedDemonstrativePronouns.delete(protoHead!);
        } else if (entry.paradigm === "personal-pronouns") {
          this._unusedPersonalPronouns.delete(protoHead!);
        }
      }
    }

    const linguistInfo: CreeLinguistInfo = {};
    if (pos) {
      linguistInfo.inflectional_category = pos;
      // pos in the toolbox/ndjson has a different meaning from in the python
      // code
      linguistInfo.pos = posFromInflectionalCategory(pos);
    }
    const stem = obj.dataSources?.CW?.stm;
    if (stem) {
      linguistInfo.stem = stem;
    }
    if (protoHead !== head) {
      linguistInfo.proto_cree = protoHead;
    }

    entry.linguistInfo = linguistInfo;

    for (const sourceAbbreviation in obj.dataSources) {
      if (this.shouldSkipSource(sourceAbbreviation)) {
        continue;
      }
      for (const sense of obj.dataSources[sourceAbbreviation].senses) {
        entry.addDefinition(sense.definition, [sourceAbbreviation]);
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

  async save(options: { pretty: boolean }) {
    if (this._unusedDemonstrativePronouns.size !== 0) {
      throw new Error(
        `Unused demonstrative pronouns: ${[
          ...this._unusedDemonstrativePronouns,
        ].join(", ")}`
      );
    }
    if (this._unusedPersonalPronouns.size !== 0) {
      throw new Error(
        `Unused personal pronouns: ${[...this._unusedPersonalPronouns].join(
          ", "
        )}`
      );
    }

    await writeFile(this._outputFileName, this._dictionary.assemble(options));
    console.log(`Wrote ${this._outputFileName}`);
  }

  abstract protoCreeToInternalOrthography(s: string): string;

  /**
   * Hook function for pre-filtering entries.
   */
  shouldSkipNdjsonEntry(obj: NdjsonEntry) {
    return false;
  }

  /**
   * Hook function for filtering out definition sources.
   */
  shouldSkipSource(abbreviation: string) {
    return false;
  }
}

export class CrkImport extends Import {
  protoCreeToInternalOrthography(s: string) {
    return protoToPlains(s);
  }
}

export class CwdImport extends Import {
  protoCreeToInternalOrthography(s: string) {
    return protoToWoods(s);
  }

  shouldSkipNdjsonEntry(obj: NdjsonEntry) {
    // Skip MD-only entries for Woods Cree
    if (isEqual(Object.keys(obj.dataSources), ["MD"])) {
      return true;
    }
    return super.shouldSkipNdjsonEntry(obj);
  }

  shouldSkipSource(sourceAbbrevation: string): boolean {
    // No Maskwacîs entries for the Woods Cree dictionary.
    if (sourceAbbrevation === "MD") {
      return true;
    }

    return super.shouldSkipSource(sourceAbbrevation);
  }
}
