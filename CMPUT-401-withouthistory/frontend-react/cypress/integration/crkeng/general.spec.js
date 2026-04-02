/**
 * General tests about the website's behaviour as a regular website.
 */
context("General", function () {
  beforeEach(function () {
    cy.visit("http://10.2.10.152/");
  });

  describe("Visiting the home page", () => {
    it("should say “itwêwina” in the header", () => {
      cy.get("h1").should("be.visible").should("contain", "itwêwina");
    });

    it("should greet the users in the content", () => {
      cy.get("main")
        .contains("h1, h2", /\bt[âā]n[i']?si\b/)
        .should("be.visible");
    });
  });

  // TODO reenable when welcome page supports syllabics
  // describe("I want see all written Cree in Western Cree Syllabics", function () {
  //   it("should be accessible from the language selector", function () {
  //     cy.get("[data-cy=settings-menu]")
  //       // this should be `.type('{enter}')` but that mysteriously fails when
  //       // running cypress against firefox on Ubuntu, even though pressing enter
  //       // in the browser *does* work. Workaround is to click() instead.
  //       .click();

  //     cy.get("[data-cy=orthography-choices]")
  //       .should("be.visible")
  //       .contains("Syllabics")
  //       .click();

  //     cy.get("h1").contains("ᐃᑘᐏᓇ");
  //   });
  // });
});
