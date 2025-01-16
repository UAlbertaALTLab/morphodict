import urls from "../../support/urls";

describe("The Tsúūt'ínà site", function () {
  it("works", function () {
    cy.visit(`${urls.srseng}`);
    cy.get(".branding__heading").contains("Gūnáhà");
  });

  it("can search for a word", function () {
    cy.visitSearch(`yidiskid`, urls.srseng).searchResultsContain("yídiskid");
  });

  it("can display a paradigm", function () {
    cy.visit(`${urls.srseng}/word/yídiskid`);
    cy.get(".paradigm-cell").contains("mídiskid");
  });
});
