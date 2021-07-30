import { expect } from "chai";
import { Dictionary, Wordform } from "../shared/dictionary";
import { removeMdOnlyEntries } from "./cwdize";

describe("cwdize", function () {
  describe("removeMdOnlyEntries", function () {
    it("removes the expected stuff", function () {
      const dictionary = new Dictionary();

      let word1 = dictionary.getOrCreate({ text: "word1" });
      word1.senses = [
        { definition: "md-only", sources: ["MD"] },
        { definition: "shared", sources: ["CW", "MD"] },
        { definition: "cw-only", sources: ["CW"] },
      ];
      let word2 = dictionary.getOrCreate({ text: "word2" });
      word2.senses = [{ definition: "md-only", sources: ["MD"] }];

      const word2form = new Wordform<never>();
      word2form.head = "word2-form";
      word2form.senses = [{ definition: "foo", sources: ["CW"] }];
      word2form.formOf = word2;
      dictionary.addWordform(word2form);

      removeMdOnlyEntries(dictionary);

      expect([...dictionary]).to.eql([
        {
          head: "word1",
          senses: [
            { definition: "shared", sources: ["CW"] },
            { definition: "cw-only", sources: ["CW"] },
          ],
        },
      ]);
    });
  });
});
