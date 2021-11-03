import { expect } from "chai";
import { Dictionary, Wordform } from "../shared/dictionary";
import { munge, NdjsonDatabase, removeMdOnlyEntries } from "./cwdize";

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

  describe("munge", function () {
    it("works on a basic input", function () {
      const inputCrkengImportJson = [
        {
          head: "asiskîwiyâkanihkamawêw",
          analysis: [
            [],
            "asiskîwiyâkanihkamawêw",
            ["+V", "+TA", "+Ind", "+3Sg", "+4Sg/PlO"],
          ],
          paradigm: "VTA",
          senses: [
            {
              definition: "s/he makes pottery for s.o.",
              sources: ["CW"],
            },
          ],
          linguistInfo: {
            inflectional_category: "VTA-2",
            pos: "V",
            stem: "asiskîwiyâkanihkamaw-",
            wordclass: "VTA",
          },
          slug: "asiskîwiyâkanihkamawêw",
        },
        {
          head: "ayâw",
          analysis: [[], "ayâw", ["+V", "+II", "+Ind", "+3Sg"]],
          paradigm: "VII",
          senses: [
            {
              definition: "it is, it is there",
              sources: ["CW"],
            },
          ],
          linguistInfo: {
            inflectional_category: "VII-2v",
            pos: "V",
            stem: "ayâ-",
            wordclass: "VII",
          },
          slug: "ayâw@vii",
        },

        // An entry with an associated wordform
        {
          head: "mâyiskawêw",
          analysis: [
            [],
            "mâyiskawêw",
            ["+V", "+TA", "+Ind", "+3Sg", "+4Sg/PlO"],
          ],
          paradigm: "VTA",
          senses: [
            {
              definition:
                "s/he affects s.o. negatively, s/he has an adverse effect on s.o.; s/he makes s.o. ill; s/he is not suited to s.o., s/he does not fit in with s.o.",
              sources: ["CW"],
            },
          ],
          linguistInfo: {
            inflectional_category: "VTA-2",
            pos: "V",
            stem: "mâyiskaw-",
            wordclass: "VTA",
          },
          slug: "mâyiskawêw",
        },
        {
          head: "mâyiskâkow",
          analysis: [
            [],
            "mâyiskawêw",
            ["+V", "+TA", "+Ind", "+4Sg/Pl", "+3SgO"],
          ],
          senses: [
            {
              definition:
                "it affects s.o. badly, it has an adverse effect on s.o.; it makes s.o. ill, it makes s.o. react allergically",
              sources: ["CW"],
            },
          ],
          formOf: "mâyiskawêw",
        },
      ];

      const inputCrkengNdjson = new NdjsonDatabase([
        {
          dataSources: {
            CW: {
              pos: "VTA-2",
              senses: [{ definition: "s/he makes pottery for s.o." }],
            },
          },
          lemma: {
            proto: "asiskîwiýâkanihkamawêw",
            sro: "asiskîwiyâkanihkamawêw",
          },
        },
        {
          dataSources: {
            CW: {
              pos: "VII-2v",
              senses: [{ definition: "it is, it is there" }],
            },
          },
          lemma: { proto: "ayâw", sro: "ayâw" },
        },
        {
          dataSources: {
            CW: {
              pos: "VTA-2",
              senses: [
                {
                  definition:
                    "s/he affects s.o. negatively, s/he has an adverse effect on s.o.",
                },
                { definition: "s/he makes s.o. ill" },
                {
                  definition:
                    "s/he is not suited to s.o., s/he does not fit in with s.o.",
                },
              ],
            },
          },
          lemma: { proto: "mâýiskawêw", sro: "mâyiskawêw" },
        },
        {
          dataSources: {
            CW: {
              pos: "VTA-2",
              senses: [
                {
                  definition:
                    "it affects s.o. badly, it has an adverse effect on s.o.",
                },
                {
                  definition:
                    "it makes s.o. ill, it makes s.o. react allergically",
                },
              ],
            },
          },
          lemma: { proto: "mâýiskâkow", sro: "mâyiskâkow" },
        },
      ]);

      const munged = munge(
        Dictionary.fromJson(JSON.stringify(inputCrkengImportJson)),
        inputCrkengNdjson
      );

      expect(JSON.parse(munged)).to.eql([
        {
          head: "asiskîwithâkanihkamawîw",
          analysis: [
            [],
            "asiskîwithâkanihkamawîw",
            ["+V", "+TA", "+Ind", "+3Sg", "+4Sg/PlO"],
          ],
          paradigm: "VTA",
          senses: [
            {
              definition: "s/he makes pottery for s.o.",
              sources: ["CW"],
            },
          ],
          linguistInfo: {
            inflectional_category: "VTA-2",
            pos: "V",
            proto: "asiskîwiýâkanihkamawêw",
            // FIXME: stem requires crk-db code to include proto stem
            stem: "asiskîwiyâkanihkamaw-",
            wordclass: "VTA",
          },
          slug: "asiskīwithākanihkamawīw",
        },
        {
          analysis: [[], "ayâw", ["+V", "+II", "+Ind", "+3Sg"]],
          head: "ayâw",
          linguistInfo: {
            inflectional_category: "VII-2v",
            pos: "V",
            stem: "ayâ-",
            wordclass: "VII",
          },
          paradigm: "VII",
          senses: [
            {
              definition: "it is, it is there",
              sources: ["CW"],
            },
          ],
          slug: "ayâw@vii",
        },
        {
          head: "mâthiskawîw",
          analysis: [
            [],
            "mâthiskawîw",
            ["+V", "+TA", "+Ind", "+3Sg", "+4Sg/PlO"],
          ],
          paradigm: "VTA",
          senses: [
            {
              definition:
                "s/he affects s.o. negatively, s/he has an adverse effect on s.o.; s/he makes s.o. ill; s/he is not suited to s.o., s/he does not fit in with s.o.",
              sources: ["CW"],
            },
          ],
          linguistInfo: {
            inflectional_category: "VTA-2",
            pos: "V",
            proto: "mâýiskawêw",
            stem: "mâyiskaw-",
            wordclass: "VTA",
          },
          slug: "māthiskawīw",
        },
        {
          head: "mâthiskâkow",
          analysis: [
            [],
            "mâthiskawîw",
            ["+V", "+TA", "+Ind", "+4Sg/Pl", "+3SgO"],
          ],
          senses: [
            {
              definition:
                "it affects s.o. badly, it has an adverse effect on s.o.; it makes s.o. ill, it makes s.o. react allergically",
              sources: ["CW"],
            },
          ],
          formOf: "māthiskawīw",
        },
      ]);
    });
  });
});
