import urls from "../../support/urls";

describe("The Tsúūt'ínà site", function () {
  it("works", function () {
    cy.visit(`${urls.srseng}`);
    cy.get(".branding__heading").contains("Gūnáhà");
  });

  it("can search for a word", function () {
    cy.visitSearch(`nas7in`, urls.srseng).searchResultsContain("násʔín");
  });

  it("can display a paradigm", function () {
    cy.visit(`${urls.srseng}/word/násʔín`);
    cy.get(".paradigm-cell").contains("gīmīts'īnáyísʔìn");
  });
});
