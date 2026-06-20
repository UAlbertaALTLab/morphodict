/**
 * General tests about the website's behaviour as a regular website.
 */
context("The About page", function () {
  describe("Visiting any page", () => {
    it("should have a link to the about page in the footer", () => {
      cy.visit("http://10.2.10.152");
      cy.get("footer").contains("a", "About");
    });
  });

  beforeEach(function () {
    cy.visit("http://10.2.10.152/about");
  });

  describe("Visiting the about page", () => {
    it("should have a few required sections", () => {
      cy.get("main").contains("h2", /Source Materials/i);
      cy.get("main").contains("h2", "Credits");
      cy.get("main").contains("h2", /Contact Us/i);
    });

    it("should have a mailto link", () => {
      cy.contains("altlab@ualberta.ca");
    });

    it("should have an href in the mailto link", () => {
      cy.contains("section#contact-us", "altlab@ualberta.ca");
    });
    it("should have partner logos", () => {
      cy.get("main .partner-logos").should("be.visible").as("logos");

      cy.get("@logos").get('img[alt="MESC"]');
      cy.get("@logos").get('img[alt="University of Alberta"]');
      cy.get("@logos").get('img[alt="National Research Council Canada"]');
      cy.get("@logos").get('img[alt="First Nations University"]');
      cy.get("@logos").get(
        'img[alt="Social Sciences and Humanities Research Council"]'
      );
    });
  });

  describe("Visiting the contact us page", function () {
    it("should have a mailto: link to the altlab email address", function () {
      cy.visit("http://10.2.10.152/contact-us");
      cy.contains("a", "altlab@ualberta.ca")
        // email address is an alias with '+', useful for email filtering.
        .should("have.attr", "href", "mailto:altlab+itwewina@ualberta.ca");
    });

    //SMALL ISSUE (DOESN'T want to clikc on contact us link)
    // it("should be linked in the footer", function () {
    //   cy.visit("http://10.2.10.152");

    //   cy.get('a[href*="Contact-us"').click();

    //   cy.url().should("contain", "/contact-us");
    // });
  });
});
