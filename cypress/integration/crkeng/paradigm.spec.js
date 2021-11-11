describe("I want to search for a Cree word and see its inflectional paradigm", () => {
  // Test at least one word from each word class:
  const testCases = [
    {
      pos: "VTA",
      lemma: "mowêw",
      inflections: ["kimowin", "kimowitin", "ê-mowât"],
    },
    {
      pos: "VAI",
      lemma: "wâpiw",
      inflections: ["niwâpin", "kiwâpin", "ê-wâpiyit"],
    },
    {
      pos: "VTI",
      lemma: "mîcisow",
      inflections: ["nimîcison", "kimîcison", "ê-mîcisoyit"],
    },
    { pos: "VII", lemma: "nîpin", inflections: ["nîpin", "ê-nîpihk"] },
    { pos: "NAD", lemma: "nôhkom", inflections: ["kôhkom", "ohkoma"] },
    { pos: "NID", lemma: "mîpit", inflections: ["nîpit", "kîpit", "wîpit"] },
    { pos: "NA", lemma: "minôs", inflections: ["minôsak", "minôsa"] },
    {
      pos: "NI",
      lemma: "nipiy",
      inflections: ["nipîhk", "ninipiy", "kinipiy"],
    },
  ];

  // Create test cases for each word above
  for (let { pos, lemma, inflections } of testCases) {
    it(`should display the paradigm for a word belonging to the ${pos} word class`, () => {
      cy.visitSearch(lemma);
      cy.get("[data-cy=search-results]").contains("a", lemma).click();

      cy.get("[data-cy=paradigm]").as("paradigm");

      let ctx = cy.get("@paradigm").should("contain", lemma);
      for (let wordform of inflections) {
        ctx = ctx.and("contain", wordform);
      }
    });
  }

  it("should display the paradigm for personal pronouns", () => {
    const head = "niya";
    const inflections = ["kiya", "wiya"];

    cy.visitSearch(head);
    cy.get("[data-cy=search-results]").contains("a", head).click();

    cy.get("[data-cy=paradigm]").as("paradigm");

    let ctx = cy.get("@paradigm").should("contain", head);
    for (let wordform of inflections) {
      ctx = ctx.and("contain", wordform);
    }

    const labels = [
      { scope: "col", label: /\bone\b/i },
      { scope: "col", label: /\bmany\b/i },
      { scope: "row", label: "I" },
      { scope: "row", label: /\byou\b/i },
    ];

    for (let { scope, label } of labels) {
      cy.get("@paradigm")
        .contains("th", label)
        .should("have.attr", "scope", scope);
    }
  });

  // TODO: the next test should be here, but it is broken because the
  // upstream layouts are broken :/
  it.skip("should display titles within the paradigm", () => {
    // TODO: move this test into the previous test when the layout is fixed.
    cy.visitSearch("minôsis");
    cy.get("[data-cy=search-results]").contains("a", "minôsis").click();

    cy.get("[data-cy=paradigm]").as("paradigm");

    // TODO: the layouts should be able to differentiate between titles and
    // labels; currently, the specificiation is ambigous, hence, it's seen
    // as a .paradigm-label, when it should be a .paradigm-title :/
    cy.get("@paradigm").contains(".paradigm-title", "Ownership");
  });
});

describe("I want to know if a form is observed inside a paradigm table", () => {
  // TODO: this test should be re-enabled in linguist mode!
  it.skip("shows inflection frequency as digits in brackets", () => {
    cy.visitLemma("nipâw");
    cy.get("[data-cy=paradigm]").contains(/\(\d\)/);
  });
});

describe("I want to see a clear indicator that a form does not exist", () => {
  it("shows cells that do not exist as an em dash", () => {
    const EM_DASH = "—";

    // minôs does NOT have a diminutive
    cy.visitLemma("minôs");
    cy.get("[data-cy=paradigm]").contains("td", EM_DASH);
  });
});

describe("paradigms are visitable from link", () => {
  const lemmaText = "niska";
  it("shows basic paradigm", () => {
    cy.visitLemma(lemmaText, { analysis: "niska+N+A+Sg" });
    // "Smaller" should be in the plain English labeling
    cy.get("[data-cy=paradigm]").contains(/\bSmaller\b/i);
  });

  it("shows full paradigm", () => {
    cy.visitLemma(lemmaText, {
      analysis: "niska+N+A+Sg",
      "paradigm-size": "FULL",
    });
    // his/her/their is an exclusive user friendly tag for FULL paradigms
    cy.get("[data-cy=paradigm]").contains("his/her/their");
  });
});

describe("paradigms can be toggled by the show more/less button", () => {
  it("shows basic, full, linguistic, and basic paradigm in sequence", () => {
    cy.visitLemma("nipâw");

    const basicForm = "ninipân"; // Basic, first person singular form
    const fullForm = "ê-kî-nipâyêk"; // past, conjunct, second person plural form -- not basic!

    // Initially, we should be on the **basic** size
    paradigm().contains("td", basicForm);
    paradigm().contains("td", fullForm).should("not.exist");

    // Switch to the full size
    cy.get("[data-cy=paradigm-toggle-button]").click();
    cy.location("search").should("match", /\bfull\b/i);

    paradigm().contains("td", basicForm);
    paradigm().contains("td", fullForm);

    // Switch once more to get back to the basic paradigm
    cy.get("[data-cy=paradigm-toggle-button]").click();
    cy.location("search").should("match", /\bbasic\b/i);

    function paradigm() {
      return cy.get("[data-cy=paradigm]");
    }
  });
});

describe("Paradigm labels", () => {
  let lemma = "nipâw";
  let englishLabel = "they";
  let nehiyawewinLabel = "wiyawâw";
  let linguisticLabel = "3p";

  it("should appear in plain English by default", () => {
    cy.visitLemma(lemma, { "paradigm-size": "FULL" });

    cy.get("[data-cy=paradigm]").contains("th[scope=row]", englishLabel);
  });

  it("should appear in nêhiyawêwin (Plains Cree)", () => {
    cy.visitLemma(lemma, { "paradigm-size": "FULL" });

    cy.get("[data-cy=open-paradigm-label-switcher]").click();
    cy.get("[data-cy=paradigm-label-options]")
      .contains(/nêhiyawêwin/i)
      .click();

    cy.get("[data-cy=paradigm]").contains("th[scope=row]", nehiyawewinLabel);
  });

  it("should appear using lingustic terminology", () => {
    cy.visitLemma(lemma, { "paradigm-size": "FULL" });

    cy.get("[data-cy=open-paradigm-label-switcher]").click();
    cy.get("[data-cy=paradigm-label-options]")
      .contains(/linguistic/i)
      .click();

    cy.get("[data-cy=paradigm]").contains("th[scope=row]", linguisticLabel);
  });
});

describe("I want to see multiple variants of the same inflection on multiple rows", () => {
  // See: https://github.com/UAlbertaALTLab/morphodict/issues/507
  it("should display two rows for nipâw+V+AI+Ind+12Pl", () => {
    const forms = ["kinipânaw", "kinipânânaw"];
    let rowA = null;
    let rowB = null;
    cy.visitLemma("nipâw");

    // get the first row
    cy.get("[data-cy=paradigm]")
      .contains("tr", forms[0])
      .then(($form) => {
        rowA = $form.get(0);
      });

    // get the second row
    cy.get("[data-cy=paradigm]")
      .contains("tr", forms[1])
      .then(($form) => {
        rowB = $form.get(0);
      })
      .then(() => {
        expect(rowA).not.to.be.null;
        expect(rowB).not.to.be.null;

        // they should not be the same row!
        expect(rowA).not.to.equal(rowB);
      });
  });
});
