import { expect } from "chai";
import { munge } from "./toimportjson";
import { loadTsvFile } from "../shared/util";
import { join as joinPath } from "path";

describe("srseng toimportjson", function () {
  it("works on a basic input", async function () {
    const sample = await loadTsvFile(
      joinPath(__dirname, "testdata", "OS-Vocabulary sample.tsv")
    );

    const munged = munge(sample);
    expect(JSON.parse(munged)).to.eql([
      {
        head: "dītł'á",
        senses: [
          {
            definition: "he/she/it will run",
            sources: ["OS"],
          },
        ],
        analysis: [[], "dītł'á", ["+V", "+I", "+Ipfv", "+SbjSg3"]],
        paradigm: "VI",
        slug: "dītł'á",
      },
      {
        head: "dàdāàtł'á",
        analysis: [[], "dītł'á", ["+V", "+I", "+Ipfv", "+SbjPl1", "+Distr"]],
        senses: [
          {
            definition: "we each and every one will run",
            sources: ["OS"],
          },
        ],
        formOf: "dītł'á",
      },
      {
        head: "dàdāstł'á",
        analysis: [[], "dītł'á", ["+V", "+I", "+Ipfv", "+SbjPl2", "+Distr"]],
        senses: [
          {
            definition: "youᵖᴵ∙ each and every one will run",
            sources: ["OS"],
          },
        ],
        formOf: "dītł'á",
      },
      {
        head: "dāstł'á",
        analysis: [[], "dītł'á", ["+V", "+I", "+Ipfv", "+SbjPl2"]],
        senses: [
          {
            definition: "youᵖˡ∙ will run",
            sources: ["OS"],
          },
        ],
        formOf: "dītł'á",
      },
    ]);
  });
});
