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
    it('shows VTA', function () {
      cy.debug()
    })
  })
})
