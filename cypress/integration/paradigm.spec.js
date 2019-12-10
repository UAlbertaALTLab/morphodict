context('Paradigms', () => {
  describe(' I want to search for a Cree word and see its inflectional paradigm', () => {
    const testCases = [
      {pos: 'VTA', lemma: 'mowêw', inflections: ['kimowin', 'kimowitin', 'ê-mowât']},
      {pos: 'NA', lemma: 'minôs', inflections: ['minôsak', 'minôsa']},
    ]

    // Create test cases for each word above
    for (let {pos, lemma, inflections} of testCases) {
      it(`should display the paradigm for an ${pos} word`, () => {
        cy.visit(`/search/${lemma}`)
        cy.get('[data-cy=search-results]')
          .contains('a', lemma)
          .click()

        cy.get('[data-cy=paradigm]')
          .as('paradigm')

        let ctx = cy.get('@paradigm')
          .should('contain', lemma)
        for (let wordform of inflections) {
          ctx = ctx.and('contain', wordform)
        }
      })
    }

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
