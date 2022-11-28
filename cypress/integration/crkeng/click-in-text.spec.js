describe("click-in-text", function () {
  beforeEach(function () {
    cy.visit("/click-in-text-embedded-test");
    cy.wait(1000);
  });

  function withPopupDivs(popupDivsHandler) {
    cy.get("transover-popup").should((popups) => {
      expect(popups.length).to.eql(1);
      const popup = popups[0];
      const divs = Cypress.$(popup.shadowRoot.querySelectorAll("div"));
      popupDivsHandler(divs);
    });
  }

  it.skip("works on Cree words", function () {
    cy.contains("span", "wâpamêw").click();
    withPopupDivs((popupDivs) => {
      expect(popupDivs).to.be.visible;
      expect(popupDivs).to.contain("s/he sees s.o");
      expect(popupDivs).to.contain("s/he witnesses s.o");
    });
  });

  it.skip("works on English words", function () {
    cy.contains("span", "hello").click();
    withPopupDivs((popupDivs) => {
      expect(popupDivs).to.be.visible;
      expect(popupDivs).to.contain("tânisi");
      expect(popupDivs).to.contain("atamiskawêw");
    });
  });
});
