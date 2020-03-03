describe('Orthography selection', function () {
  describe('switching orthography', function () {
    it('should switch to syllabics when I click on the menu', function () {
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
        .should('be.visible')
        .click()

      // Now it should be in syllabics!
      cy.get('@greeting')
        .contains('ᑖᓂᓯ!')
    })
  })
})
