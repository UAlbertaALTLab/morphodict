import { skipOn } from "@cypress/skip-test";

describe("Orthography selection", function () {
  describe("switching orthography", function () {
    it("should switch to syllabics when I click on the menu", function () {
      cy.visit("/");

      // Get the introduction: it should be in SRO
      cy.contains("h2", "tânisi").as("greeting");

      // Switch to syllabics
      cy.get("[data-cy=settings-menu]").click().parent("details").as("menu");
      cy.get("@menu")
        .contains("Syllabics")
        .as("option")
        .should("be.visible")
        .click();

      // Now it should be in syllabics!
      cy.get("@greeting").contains("ᑖᓂᓯ");

      // It should say so on the button
      cy.get("[data-cy=settings-menu]").click();

      // Opening the menu, we should find that syllabics is highligted, and
      // SRO is not:
      cy.get("@menu")
        .contains("li", "SRO (êîôâ)")
        .should("not.have.class", "menu-choice--selected");
      cy.get("@menu")
        .contains("li", "Syllabics");
    });

    it("should display in syllabics given the correct cookies", function () {
      let settings = {
        "plainEngl":true,"lingLabel":false,"niyaLabel":false,"label":"ENGLISH","emojis":{"man":"🧑🏽","gamma":"👵🏽","gapa":"👴🏽","wolf":"🐺","bear":"🐻","bread":"🍞","star":"🌟"},"active_emoji":"🧑🏽","cw_source":false,"md_source":false,"aecd_source":false,"all_sources":true,"latn":false,"latn_x_macron":false,"syllabics":true,"currentType":"Cans","showAudio":false,"synthAudio":false,"synthAudioParadigm":false,"espt":false,"autoTranslate":false,"showEmoji":true,"showIC":true,"morphemes_everywhere":false,"morphemes_headers":false,"morphemes_paradigms":false,"morphemes_nowhere":true,"md_audio":false,"mos_audio":false,"both_audio":true,"cmro":false}

      window.localStorage.setItem('settings', JSON.stringify(settings));
      window.dispatchEvent(new Event("settings"));

      // Visiting a page should be in syllabics
      cy.visit("/about");
      cy.contains("h1", "ᐃᑘᐏᓇ");
    });

    it("should persist my preference after a page load", function () {
      // XXX: This test fails in headless mode for Electron version < v6.0
      // There was a bug with setting cookies via fetch():
      //    https://github.com/cypress-io/cypress/issues/4433
      // This should work in Cypress 3.5.0 using Chrome.
      // TODO: switch CI to use Chrome instead of Electron!
      skipOn("electron");

      cy.visit("/");

      // Get the introduction: it should be in SRO
      cy.contains("h2", "tânisi").as("greeting");

      // Switch to syllabics
      cy.get("[data-cy=settings-menu]").click().parent("details").as("menu");
      cy.get("@menu").contains("Syllabics").click();

      // It changed on the current page:
      cy.get("@greeting").contains("ᑖᓂᓯ");

      // Now try a different page.
      cy.visit("/about");

      // It should be in syllabics.
      cy.contains("h1", "ᐃᑘᐏᓇ");
    });

    it.skip("should display Cree examples in syllabics", function () {
      cy.setCookie("orth", "Cans");

      // Visiting a page should be in syllabics
      cy.visitSearch("ᓃᒥᓈᓂᐘᐣ");
      cy.contains("[data-cy=elaboration]", "like: ᓂᐹᐤ");
    });
  });
});
