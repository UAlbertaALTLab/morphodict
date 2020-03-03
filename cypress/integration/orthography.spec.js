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

      // It should say so on the button
      cy.get('[data-cy=language-selector]')
        .contains('Syllabics')

      // We should no longer be able to see options
      cy.get('@option')
        .should('not.be.visible')
    })
  })
})
