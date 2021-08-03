import { expect } from "chai";
import { ArapahoLexiconEntry, AraphoLexicon, munge } from "./toimportjson";

// Allow test inputs to both include a bunch of extra stuff copied from
// original, and, for testing purposes, inputs missing required fields
type LooseArapahoLexicon = {
  [id: string]: Partial<ArapahoLexiconEntry> & { [key: string]: unknown };
};

describe("arpeng toimportjson", function () {
  it("works on a basic input", function () {
    const munged = munge((({
      L16737: {
        semantic_domain: "",
        image: "",
        pos: "vii",
        parent_lex: "",
        examples: [],
        morphology: "nihoon-yoo-",
        examplefrequency: 0,
        gloss: "yellow",
        etymology: "",
        literal: "",
        allolexemes: [
          "niihooyoo-",
          "niihooyou'-",
          "niihooyóó- IC",
          "nihooyoo-",
        ],
        usage_main: "",
        status: "",
        base_form: "níhooyóó-",
        senses: [
          {
            definition: "yellow",
          },
        ],
        cultural: "",
        user: "",
        lex: "nihooyoo-",
        date_added: "2011-04-29 00:00:00",
        parent_lexid: "",
        parent_rel: "",
        sound: [
          "http://verbs.colorado.edu/~ghka9436/audiovisual/audio/n/heet-nihooyoo-'.mp3",
          "http://verbs.colorado.edu/~ghka9436/audiovisual/audio/n/nihooyoo-'.mp3",
        ],
        language: "Arapaho",
        date_modified: "2016-01-14 14:36:40",
        derivations: [],
      },
      // Entries marked deleted should be skipped
      L23962: {
        status: "deleted",
      },
      // the IC version, with an additional definition, should end up linked
      L16276: {
        semantic_domain: "",
        image: "",
        pos: "vai",
        parent_lex: "",
        examples: [],
        morphology: "ni'-i-3ecoo-",
        examplefrequency: 0,
        gloss: "glad, happy",
        etymology: "",
        literal: "",
        allolexemes: ["nii'í3ecóó- IC", "ni'i3ecoo-"],
        usage_main: "",
        status: "",
        base_form: "ni'í3ecóó-",
        senses: [
          {
            definition: "glad, happy",
          },
        ],
        cultural: "",
        user: "",
        lex: "ni'i3ecoo-",
        date_added: "2014-09-09 00:00:00",
        parent_lexid: "",
        parent_rel: "",
        sound: [
          "http://verbs.colorado.edu/~ghka9436/audiovisual/audio/n/heetih-ni'i3ecoo-3i'.wav",
          "http://verbs.colorado.edu/~ghka9436/audiovisual/audio/n/ni'i3ecoo-3i'.mp3",
          "http://verbs.colorado.edu/~ghka9436/audiovisual/audio/n/ni'i3ecoo-n.mp3",
          "http://verbs.colorado.edu/~ghka9436/audiovisual/audio/n/ni'i3ecoo-ni'.mp3",
          "http://verbs.colorado.edu/~ghka9436/audiovisual/audio/n/ni'i3ecoo-no'.mp3",
          "http://verbs.colorado.edu/~ghka9436/audiovisual/audio/n/ni'i3ecoo-noo.mp3",
          "http://verbs.colorado.edu/~ghka9436/audiovisual/audio/n/ni'i3ecoo-noo3.mp3",
          "http://verbs.colorado.edu/~ghka9436/audiovisual/audio/n/ni'i3ecoo-t.mp3",
        ],
        language: "Arapaho",
        date_modified: "2016-09-25 17:40:12",
        derivations: [],
      },
      L16792: {
        semantic_domain: "",
        image: "",
        pos: "vti",
        parent_lex: "",
        examples: [],
        morphology: "ni'-i-3ecoo-:t-",
        examplefrequency: 0,
        gloss: "IC.enjoy s.t.",
        etymology: "",
        literal: "",
        allolexemes: ["nii'i3ecoot-"],
        usage_main: "",
        status: "",
        base_form: "nii'í3ecóot-",
        senses: [
          {
            definition: "IC.enjoy s.t.",
          },
        ],
        cultural: "",
        user: "",
        lex: "nii'i3ecoot-",
        date_added: "2009-03-20 00:00:00",
        parent_lexid: "",
        parent_rel: "allolexeme",
        sound: "",
        language: "Arapaho",
        date_modified: "2009-03-20 00:00:00",
        derivations: [],
      },
    } as LooseArapahoLexicon) as any) as AraphoLexicon);

    expect(JSON.parse(munged)).to.eql([
      {
        analysis: [
          ["[VERB]", "[AI]", "[ANIMATE-SUBJECT]", "[IMPERATIVE]"],
          "ni'i3ecoo",
          ["[2SG-SUBJ]"],
        ],
        head: "ni'í3ecóó-",
        linguistInfo: {
          morphologies: ["ni'-i-3ecoo-"],
          pos: "vai",
          sourceIds: ["L16276"],
        },
        paradigm: "AI",
        senses: [
          {
            definition: "glad, happy",
            sources: ["ALD"],
          },
        ],
        slug: "ni'í3ecóó-",
      },
      {
        analysis: [
          [
            "[VERB]",
            "[AI]",
            "[ANIMATE-SUBJECT]",
            "[AFFIRMATIVE]",
            "[PRESENT]",
            "[IC]",
          ],
          "ni'i3ecoo",
          ["[3SG-SUBJ]"],
        ],
        formOf: "ni'í3ecóó-",
        head: "nii'í3ecóot-",
        senses: [
          {
            definition: "IC.enjoy s.t.",
            sources: ["ALD"],
          },
        ],
      },
      {
        head: "níhooyóó-",
        linguistInfo: {
          pos: "vii",
          sourceIds: ["L16737"],
          morphologies: ["nihoon-yoo-"],
        },
        senses: [
          {
            definition: "yellow",
            sources: ["ALD"],
          },
        ],
        fstLemma: "nihooyoo",
        paradigm: "II",
        slug: "níhooyóó-",
      },
    ]);
  });
});
