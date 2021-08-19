import { readFile } from "fs/promises";
import { NdjsonEntry } from "./cwdize";

export async function readNdjsonFile(path: string): Promise<NdjsonEntry[]> {
  const ret = [];
  const text = await readFile(path, "utf8");
  for (const piece of text.split("\n")) {
    if (!piece) {
      continue;
    }
    ret.push(JSON.parse(piece) as NdjsonEntry);
  }
  return ret;
}
