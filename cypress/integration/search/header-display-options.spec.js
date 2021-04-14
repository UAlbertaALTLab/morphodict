/**
 * Similar to ./result-header.spec.js -- displays a more deta
 */
context('Searching', () => {
  after(() => {
    cy.visit('/')
    cy.get('[data-cy=enable-basic-mode]')
      .click()
  })

  // See: https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/445#:~:text=4.%20Inflected%20form
  context('result header', function () {
    const lemma = 'mîciw'
    const inflectionalClass = 'VTI-3'

    it('shows the inflectional class in linguistic mode', function () {
      cy.visitSearch(lemma)
      cy.get('[data-cy=search-result]:first')
        .contains(inflectionalClass)
        .should('not.be.visible')

      cy.get('[data-cy=enable-basic-mode]')
        .click()

      cy.get('[data-cy=search-result]:first')
        .contains(inflectionalClass)
        .should('be.visible')
    })
  })
})
