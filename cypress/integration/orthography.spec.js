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
    

    it('should persist my preference after a page load', function () {
      cy.visit('/')

      // Get the introduction: it should be in SRO
      cy.contains('h1', 'tânisi!')
        .as('greeting')

      // Switch to syllabics
      cy.get('[data-cy=language-selector]')
        .click()
        .parent('details')
        .as('menu')
      cy.get('@menu')
        .contains('Syllabics')
        .click()

      // It changed on the current page:
      cy.get('@greeting')
        .contains('ᑖᓂᓯ!')

      // Now try a different page. It should be in syllabics.
      cy.visit('/about')
      cy.contains('.prose_heading', 'ᓀᐦᔭᐍᐏᐣ')
    })
  })
})
