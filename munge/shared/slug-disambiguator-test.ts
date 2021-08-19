import { expect } from "chai";
import { disambiguateSlugs } from "./slug-disambiguator";

function stringify(strings: string[]) {
  return strings.map((s) => JSON.stringify(s)).join(", ");
}

describe("disambiguateSlugs", function () {
  for (const [inputs, expectedOutputs] of [
    [["XYZ"], [""]],
    [
      ["V", "N", "N"],
      ["@v", "@n.1", "@n.2"],
    ],
    [
      ["PR", "VTI"],
      ["@p", "@v"],
    ],
    [
      ["PR", "PrA"],
      ["@pr", "@pra"],
    ],
    [
      ["PrA", "PrI"],
      ["@pra", "@pri"],
    ],
    [
      ["NA", "VTI"],
      ["@n", "@v"],
    ],
    [
      ["NA", "VAI", "VTI"],
      ["@n", "@vai", "@vti"],
    ],
    [
      ["NA", "NI"],
      ["@na", "@ni"],
    ],
    [
      ["NA", "NA"],
      ["@na.1", "@na.2"],
    ],
    [
      ["NA-1", "NA-2"],
      ["@na-1", "@na-2"],
    ],
    [
      ["VTI", "NA-1", "NA-2"],
      ["@v", "@na-1", "@na-2"],
    ],
    // we may not have anything to disambiguate the item by
    [
      ["", "", ""],
      ["@1", "@2", "@3"],
    ],
    [
      ["NA-1", ""],
      ["@n", "@1"],
    ],
  ] as [string[], string[]][]) {
    it(`returns ${stringify(expectedOutputs)} for ${stringify(
      inputs
    )}`, function () {
      expect(disambiguateSlugs(inputs)).to.eql(expectedOutputs);
    });
  }
});
