context('Paradigms', () => {
  describe(' I want to search for a Cree word and see its inflectional paradigm', () => {
    it('should display the paradigm for an VTA word', () => {
      cy.visit('/search/mowêw')
      cy.get('[data-cy=search-results]')
        .contains('a', 'mowêw')
        .click()

      cy.get('[data-cy=paradigm]')
        .as('paradigm')

      cy.get('@paradigm')
        .should('contain', 'mowêw')
        .and('contain', 'kimowin')
        .and('contain', 'kimowitin')
        .and('contain', 'ê-mowât')
    })

    it('should display the paradigm for an NA word', () => {
      cy.visit('/search/minos')
      cy.get('[data-cy=search-results]')
        .contains('a', 'minôs')
        .click()

      cy.get('[data-cy=paradigm]')
        .as('paradigm')

      cy.get('@paradigm')
        .should('contain', 'minôs')
        .and('contain', 'minôsak')
        .and('contain', 'minôsa')

      cy.get('@paradigm')
        .contains('th[scope=row]', /further/i)
    })

    // TODO: the next test should be here, but it is broken because the
    // upstream layouts are broken :/
    it.skip('should display titles within the paradigm', () => {
      // TODO: move this test into the previous test when the layout is fixed.
      cy.visit('/search/minôsis')
      cy.get('[data-cy=search-results]')
        .contains('a', 'minôsis')
        .click()

      cy.get('[data-cy=paradigm]')
        .as('paradigm')

      // TODO: the layouts should be able to differentiate between titles and
      // labels; currently, the specificiation is ambigous, hence, it's seen
      // as a .paradigm-label, when it should be a .paradigm-title :/
      cy.get('@paradigm')
        .contains('.paradigm-title', 'Ownership')
    })


  })
})
