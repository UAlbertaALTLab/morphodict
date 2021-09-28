context("Admin interface", () => {
  it("should redirect anonymous users to the login page", function () {
    cy.visit("/admin");
    cy.location().then(({ pathname }) =>
      expect(pathname).to.contain(Cypress.env("admin_login_url"))
    );
  });

  it("should allow login", function () {
    // If this test fails, you are probably using `manage.py runserver` without
    // USE_TEST_DB=True, because the `cypress` user only gets created in the
    // test database.
    cy.visit("/admin");
    cy.readCypressUserCredentials().then((cypressUser) => {
      cy.get("#id_username").type(cypressUser.username);
      cy.get("#id_password").type(cypressUser.password);
      cy.get(".submit-row > input").click();
    });
    cy.location("pathname").should("eq", Cypress.env("admin_url"));
  });

  context("auto-translations", function () {
    // NB: need to make sure this wordform is added **explicitly** in the
    // `ensuretestdb` management commands:
    let searchTerm = "niminôsak";
    let autoTranslation = "my cats";

    it("should show auto-translations to logged-in users", function () {
      cy.login();
      cy.visitSearch(searchTerm);
      cy.get("[data-cy=search-result]")
        .contains(autoTranslation)
        .get(".cite-dict")
        .contains("🤖CW");
    });

    it("should not show auto-translations to anonymous users", function () {
      cy.visitSearch(searchTerm);
      cy.get("[data-cy=search-result]").each((r) => {
        // Every result should have a dictionary citation
        cy.wrap(r)
          .get(".cite-dict")
          .should("have.length.at.least", 1)
          .each((citation) => {
            // But none of those should be auto-definitions
            cy.wrap(citation).should("not.contain", "🤖");
          });
      });
    });
  });

  specify("the FST tool should work", function () {
    cy.login();
    for (const [query, result] of [
      ["kikaniminaw", "PV/ka+nîmiw+V+AI+Ind+12Pl"],
      ["PV/ka+nîmiw+V+AI+Ind+12Pl", "kika-nîminaw"],
      ["Obv+Dim+ star", "little star over there"],
      ["Prt+3Pl+ it sings", "they sang"],
      ["they sing", "sing +V+AI+3Pl"],
    ]) {
      cy.visit("/admin/fst-tool", { qs: { text: query } });
      cy.get("pre").contains(result);
    }
  });

  it("should not show the FST tool to non-admin users", function () {
    cy.visit("/admin/fst-tool");
    cy.location().then(({ pathname }) =>
      expect(pathname).to.contain(Cypress.env("admin_login_url"))
    );
  });
});
