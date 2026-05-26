describe("Orthography selection", function () {
  describe("switching orthography", function () {
    it("should switch to syllabics when I click on the menu", function () {
      cy.visit("/");

      // Get the introduction: it should be in SRO
      cy.get("h2").as("greeting");

      cy.get("@greeting").contains("tânisi!");

      // Switch to syllabics
      cy.get("[data-cy=settings-menu]").click().parent("details").as("menu");
      cy.get("@menu")
        .contains("Syllabics")
        .as("option")
        .should("be.visible")
        .click();

      // Now it should be in syllabics!
      cy.get("@greeting").contains("ᑖᓂᓯ!");

      // It should say so on the button
      cy.get("[data-cy=settings-menu]").click();

      // Opening the menu, we should find that syllabics is highligted, and
      // SRO is not:
      cy.get("@menu")
        .contains("li", "SRO (êîôâ)")
        .should("not.have.class", "menu-choice--selected");
      cy.get("@menu")
        .contains("li", "Syllabics")
        .should("have.class", "menu-choice--selected");
    });

    it("should display in syllabics given the correct cookies", function () {
      cy.setCookie("orth", "Cans");

      // Visiting a page should be in syllabics
      cy.visit("/about");
      cy.contains("h1", "ᐃᑘᐏᓇ");
      cy.contains(".prose__heading", "ᓀᐦᐃᔭᐍᐏᐣ");
    });

    it("should persist my preference after a page load", function () {
      cy.visit("/");

      // Get the introduction: it should be in SRO
      cy.get("h2").as("greeting");
      cy.get("@greeting").contains("tânisi!");

      // Switch to syllabics
      cy.get("[data-cy=settings-menu]").click().parent("details").as("menu");
      cy.get("@menu").contains("Syllabics").click();

      // The cookies should have changed.
      cy.getCookie("orth").should("exist").its("value").should("eq", "Cans");

      // It changed on the current page:

      cy.get("@greeting").contains("ᑖᓂᓯ!");

      // Now try a different page.
      cy.visit("/about");

      // It should be in syllabics.
      cy.contains("h1", "ᐃᑘᐏᓇ");
      cy.contains(".prose__heading", "ᓀᐦᐃᔭᐍᐏᐣ");
    });

    it.skip("should display Cree examples in syllabics", function () {
      cy.setCookie("orth", "Cans");

      // Visiting a page should be in syllabics
      cy.visitSearch("ᓃᒥᓈᓂᐘᐣ");
      cy.contains("[data-cy=elaboration]", "like: ᓂᐹᐤ");
    });
  });
});
