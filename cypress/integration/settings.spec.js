context("The settings page", () => {
  it("should be accessible from the home page", () => {
    cy.visit("/");
    cy.get("[data-cy=settings-menu]")
      .click()
      .get("[data-cy=settings-link")
      .click();

    cy.url().should("match", /\bsettings\b/);
  });

  describe("setting a preference", () => {
    const PREFERENCE_COOKIE = "paradigmlabel";

    it("should set the preference without a submit button", () => {
      let checkedValue;

      cy.visit(Cypress.env("settings_url"));
      cy.clearCookie(PREFERENCE_COOKIE);

      cy.get(`input[name=${PREFERENCE_COOKIE}]`)
        .last()
        .check()
        .then((inputJquery) => {
          let input = inputJquery.get(0);
          checkedValue = input.value;
        });

      cy.get("[data-cy=toast]")
        .should("be.visible")
        .and("have.class", "toast--success");

      cy.getCookie(PREFERENCE_COOKIE).then((cookie) => {
        expect(cookie.value).to.equal(checkedValue);
      });
    });

    it("should show an error message if the save did not succeed", () => {
      cy.visit(Cypress.env("settings_url"));

      cy.get(`input[name=${PREFERENCE_COOKIE}]`)
        .parents("form")
        .then((jqueryForm) => {
          hijackFormSubmissionToAlwaysFail(jqueryForm).as("form-submission");

          cy.get(`input[name=${PREFERENCE_COOKIE}]`).last().check();
          cy.wait("@form-submission");

          cy.get("[data-cy=toast]")
            .should("be.visible")
            .and("have.class", "toast--failure");
        });

      function hijackFormSubmissionToAlwaysFail(jqueryForm) {
        return cy.intercept(
          {
            method: jqueryForm.attr("method"),
            url: jqueryForm.attr("action"),
          },
          {
            statusCode: 400,
          }
        );
      }
    });
  });
});
