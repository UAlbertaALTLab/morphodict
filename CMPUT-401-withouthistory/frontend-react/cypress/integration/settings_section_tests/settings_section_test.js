describe("Checks if show settings to the screen", () => {
  it("do we have the labels section", () => {
    cy.visit("http://10.2.10.152/cree-dictionary-settings");
    cy.contains("Paradigm labels");
    cy.contains(
      "These are the labels that appear on the paradigm table to label features like person, tense, plurals, etc."
    );
    cy.contains("Linguistic labels");
    cy.contains("Plain English labels");
    cy.contains("Nêhiyawêwin labels");
  });
});

describe("Checks if show settings to the screen", () => {
  it("do we have the emojis options", () => {
    cy.visit("http://10.2.10.152/cree-dictionary-settings");
    cy.contains("🐺");
    cy.contains("👵🏽");
    cy.contains("🍞");
  });
});

describe("Checks if show settings to the screen", () => {
  it("check if we dictionary sources", () => {
    cy.visit("http://10.2.10.152/cree-dictionary-settings");
    cy.contains("CW");
    cy.contains(
      "Show entries from the Maskwacîs Dictionary. Maskwacîs Dictionary. Maskwacîs, Maskwachees Cultural College, 1998."
    );
    cy.contains("CW-MD");
  });
});
