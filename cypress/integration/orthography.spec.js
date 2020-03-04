describe('Orthography selection', function () {
  describe('switching orthography', function () {
    it('should switch to syllabics when I click on the menu', function () {
      cy.visit('/')

      // Get the introduction: it should be in SRO
      cy.contains('h1', 'tânisi!')
        .as('greeting')

      // Switch to syllabics
      cy.get('[data-cy=language-selector]')
        .contains('SRO (êîôâ)')
        .click()
        .parent('details')
        .as('menu')
      cy.get('@menu')
        .contains('Syllabics')
        .as('option')
        .should('be.visible')
        .click()

      // Now it should be in syllabics!
      cy.get('@greeting')
        .contains('ᑖᓂᓯ!')

      // We should not see the menu
      cy.get('@option')
        .should('not.be.visible')

      // It should say so on the button
      cy.get('[data-cy=language-selector]')
        .contains('Syllabics')
        .click()

      // Opening the menu, we should find that syllabics is highligted, and
      // SRO is not:
      cy.get('@menu')
        .contains('li', 'SRO (êîôâ)')
        .should('not.have.class', 'menu-choice--selected')
      cy.get('@menu')
        .contains('li', 'Syllabics')
        .should('have.class', 'menu-choice--selected')
    })


    // XXX: This test works on my computer, but consistently fails CI.
    // I'm assuming it has something to do with setting cookies with fetch() 
    // and Electron not picking up on that, but ¯\_(ツ)_/¯
    it.skip('should persist my preference after a page load', function () {
      cy.visit('/')

      // Get the introduction: it should be in SRO
      cy.contains('h1', 'tânisi!')
        .as('greeting')

      Cypress.Cookies.debug(true)

      // Switch to syllabics
      cy.get('[data-cy=language-selector]')
        .click()
        .parent('details')
        .as('menu')
      cy.get('@menu')
        .contains('Syllabics')
        .click()

      // The cookies should have changed.
      cy.getCookie('orth')
        .should('exist')
        .its('value')
        .should('eq', 'Cans')

      // It changed on the current page:
      cy.get('@greeting')
        .contains('ᑖᓂᓯ!')

      // Now try a different page.
      cy.visit('/about')

      // It should be in syllabics.
      cy.contains('h1', 'ᐃᑘᐏᓇ')
      cy.contains('.prose__heading', 'ᓀᐦᐃᔭᐍᐏᐣ')
      cy.get('[data-cy=language-selector]')
        .contains('Syllabics')
    })
  })
})
