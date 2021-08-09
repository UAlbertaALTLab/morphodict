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

      waitForSaveConfirmation();

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

  describe("Choosing an animate emoji", () => {
    const PREFERENCE_COOKIE = "animate_emoji";
    const NON_DEFAULT_EMOJI = "🐺";

    const VTA_WORD = "mowêw";
    const NA_WORD = "minôs";
    const VAI_WORD = "nipâw";

    it("should be accessible from the settings page", () => {
      cy.getCookie(PREFERENCE_COOKIE).then((cookie) => {
        expect(cookie).to.be.null;
      });

      cy.visit(Cypress.env("settings_url"));

      cy.get("[data-cy=animate-emoji-choice]")
        .contains("label", NON_DEFAULT_EMOJI)
        .click();

      cy.getCookie(PREFERENCE_COOKIE).then((cookie) => {
        expect(cookie.value).to.be.exist;
      });
    });

    it("should changes the emoji on the search page", () => {
      cy.visit(Cypress.env("settings_url"));

      cy.get("[data-cy=animate-emoji-choice]")
        .contains("label", NON_DEFAULT_EMOJI)
        .click();

      waitForSaveConfirmation();

      // Visit the search page directly
      cy.visitSearch(VTA_WORD);
      cy.get("[data-cy=search-result]:first").contains(
        "[data-cy=word-class]",
        `${NON_DEFAULT_EMOJI}➡️${NON_DEFAULT_EMOJI}`
      );

      // On the same page, search for something else entirely
      cy.clearSearchBar().search(NA_WORD);
      cy.get("[data-cy=search-result]:first").contains(
        "[data-cy=word-class]",
        NON_DEFAULT_EMOJI
      );
    });

    it("should changes the emoji on the details page", () => {
      cy.visit(Cypress.env("settings_url"));

      cy.get("[data-cy=animate-emoji-choice]")
        .contains("label", NON_DEFAULT_EMOJI)
        .click();

      waitForSaveConfirmation();

      cy.visitLemma(VAI_WORD);
      cy.contains("[data-cy=word-class]", `${NON_DEFAULT_EMOJI}➡️`);
    });
  });

  function waitForSaveConfirmation() {
    cy.get("[data-cy=toast]")
      .should("be.visible")
      .and("have.class", "toast--success");
  }
});
