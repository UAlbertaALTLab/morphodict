import prettier from "prettier";
import assert from "assert";
import { readFile } from "fs/promises";

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
  const contents = (await readFile(path)).toString();
  const lines = contents.split("\n");
  const header = lines.shift()!.split("\t");
  const ret = [];
  for (const line of lines) {
    ret.push(Object.fromEntries(zip(header, line.split("\t"))));
  }
  return ret;
}
