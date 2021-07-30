import assert from "assert";
import { readFile } from "fs/promises";
import { resolve as resolvePath } from "path";
import prettier from "prettier";

/**
 * Run the input through the prettier tool.
 *
 * If the input is a string, it must be valid JSON; otherwise the input object
 * will be converted to JSON.
 */
export function makePrettierJson(data: unknown) {
  // Assume strings already contain JSON; otherwise, stringify
  if (typeof data !== "string") {
    data = JSON.stringify(data);
  }
  assert(typeof data === "string");
  return prettier.format(data, {
    parser: "json",
  });
}

/**
 * Return array of corresponding pairs of items from two input arrays.
 *
 * Concept borrowed from the python function of the same name.
 * https://docs.python.org/3/library/functions.html#zip
 *
 * zip([k1, k2, k3], [v1, v2, v3]) ⇒ [[k1, v1], [k2, v2], [k3, v3]]
 */
export function zip<T>(array1: T[], array2: T[]): [T, T][] {
  assert(array1.length === array2.length);
  const ret = Array(array1.length);
  for (let i = 0; i < array1.length; i++) {
    ret[i] = [array1[i], array2[i]];
  }
  return ret;
}

/**
 * Load a TSV file containing a header row, and return an array consisting of
 * one {$header: value, …} object for each row.
 */
export async function loadTsvFile(path: string) {
  const contents = await readFile(path, "utf-8");
  const lines = contents.split("\n");
  const header = lines.shift()!.split("\t");
  const ret = [];
  for (const line of lines) {
    ret.push(Object.fromEntries(zip(header, line.split("\t"))));
  }
  return ret;
}

type DefaultValueProvider<K, V> = (key: K) => V;

/**
 * A subclass of Map that automatically sets a default value when get(key) is
 * given a key not already present.
 */
export class DefaultMap<K, V> extends Map<K, V> {
  // Using `#`syntax to hide function value from console.log()
  readonly #defaultValueProvider: DefaultValueProvider<K, V>;

  constructor(defaultValueProvider: DefaultValueProvider<K, V>) {
    super();
    this.#defaultValueProvider = defaultValueProvider;
  }

  getOrCreate(key: K): V {
    if (!super.has(key)) {
      const v = this.#defaultValueProvider(key);
      super.set(key, v);
      return v;
    }
    return super.get(key)!;
  }
}

export class Counter<K = string> extends DefaultMap<K, number> {
  constructor() {
    super(() => 0);
  }

  increment(key: K, amount = 1): void {
    const oldValue = this.getOrCreate(key);
    const newValue = oldValue + amount;
    this.set(key, newValue);
  }
}

// finds non-combining character followed by combining character
const combiningRegExp = /(?<char>\P{Mark})(?<combiner>\p{Mark}+)/gu;

/**
 * Return a version of the string without diacritics or other ornamentation;
 * useful for search indexing, fuzzy matching, edit distance computations, and
 * so on.
 */
function toBaseCharacters(s: string) {
  // remove combining characters
  s = s.normalize("NFD").replace(combiningRegExp, "$1");
  s = [...s]
    .map((c) => {
      switch (c) {
        // Characters without combining decompositions. You could partly
        // automate building a table of these by looking for unicode characters
        // named “LATIN (SMALL|CAPITAL) LETTER X WITH ___”
        //
        // But as long as you’re including all the characters actually occurring
        // in your source data, you’ll be fine.
        case "ł":
          return "l";
        case "Ł":
          return "L";
        case "ɫ":
          return "l";
        case "Ɫ":
          return "l";
        default:
          return c;
      }
    })
    .join("");
  return s;
}

/**
 * Return a measure of how close two strings are to each another.
 *
 * Algorithm is similar to edit distance; see CLRS “Introduction to Algorithms” second edition, Problem 15-3.
 */
export function stringDistance(a: string, b: string) {
  const m = a.length;
  const n = b.length;
  const dist = Array(m + 1);
  for (let i = 0; i <= m; i++) {
    dist[i] = Array(n + 1);
  }

  for (let i = 0; i <= m; i++) {
    for (let j = 0; j <= n; j++) {
      if (i === 0) {
        // Edit distance between empty string and string of length j is j
        dist[i][j] = j;
      } else if (j === 0) {
        dist[i][j] = i;
      } else {
        let c = a.charAt(i - 1);
        let d = b.charAt(j - 1);

        let thisDist;

        if (c == d) {
          // exact match
          thisDist = 0;
          dist[i][j] = thisDist + dist[i - 1][j - 1];
        } else if (
          // close match
          toBaseCharacters(c).toLowerCase() ===
          toBaseCharacters(d).toLowerCase()
        ) {
          thisDist = 0.2;
          dist[i][j] = thisDist + dist[i - 1][j - 1];
        } else if (
          i >= 2 &&
          j >= 2 &&
          c === b.charAt(j - 2) &&
          d === a.charAt(i - 2)
        ) {
          // twiddle aka transposition
          thisDist = 1;
          dist[i][j] = thisDist + dist[i - 2][j - 2];
        } else {
          // no match; take the lowest edit distance possible by skipping a char
          // in one or both input strings
          thisDist = 1;
          dist[i][j] =
            thisDist +
            Math.min(dist[i - 1][j], dist[i][j - 1], dist[i - 1][j - 1]);
        }
      }
    }
  }
  return dist[m][n];
}

export function resourceDir(languagePair: string) {
  return resolvePath(__dirname, "..", "..", "src", languagePair, "resources");
}
