/**
 * Similar to ./result-header.spec.js -- displays a more deta
 */
context('Searching', () => {
  before(() => setDefaultDisplayMode())
  after(() => setDefaultDisplayMode())

  // See: https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/445#:~:text=4.%20Inflected%20form
  context('result header', function () {
    const lemma = 'mîciw'
    const inflectionalClass = 'VTI-3'

    it('shows the inflectional class in linguistic mode', function () {
      cy.visitSearch(lemma)

      inflectionalClassInDefinitionTitle()
        .should('not.exist')

      cy.get('[data-cy=enable-traditional-mode]')
        .click()

      inflectionalClassInDefinitionTitle()
        .contains(inflectionalClass)
        .should('be.visible')
    })

    function inflectionalClassInDefinitionTitle() {
      return cy.get('[data-cy=matched-wordform]:first [data-cy=inflectional-class]')
    }
  })

  function setDefaultDisplayMode() {
    cy.visit('/')
    cy.get('[data-cy=enable-basic-mode]')
      .click()
  }
})
