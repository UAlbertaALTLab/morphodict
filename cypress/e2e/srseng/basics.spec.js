import urls from "../../support/urls";

describe("The Tsúūt'ínà site", function () {
  it("works", function () {
    cy.visit(`${urls.srseng}`);
    cy.get(".branding__heading").contains("Gūnáhà");
  });

  it("can search for a word", function () {
    cy.visitSearch(`ditsa`, urls.srseng).searchResultsContain("dītsá");
  });

  it("can display a paradigm", function () {
    cy.visit(`${urls.srseng}/word/dītsá`);
    cy.get(".paradigm-cell").contains("dàts'īdītsá");
  });
});
