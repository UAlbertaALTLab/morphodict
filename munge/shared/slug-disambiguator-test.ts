import { expect } from "chai";
import { disambiguateSlugs } from "./slug-disambiguator";

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
  ] as [string[], string[]][]) {
    it(`returns ${expectedOutputs.join(", ")} for ${inputs.join(
      ", "
    )}`, function () {
      expect(disambiguateSlugs(inputs)).to.eql(expectedOutputs);
    });
  }
});
