context('Paradigms', () => {
  describe(' I want to search for a Cree word and see its inflectional paradigm', () => {
    // Test at least one word from each lexical class/part-of-speech:
    const testCases = [
      {pos: 'VTA', lemma: 'mowêw', inflections: ['kimowin', 'kimowitin', 'ê-mowât']},
      {pos: 'VAI', lemma: 'wâpiw', inflections: ['niwâpin', 'kiwâpin', 'ê-wâpiyit']},
      {pos: 'VTI', lemma: 'mîcisow', inflections: ['nimîcison', 'kimîcison', 'ê-mîcisoyit']},
      {pos: 'VII', lemma: 'nîpin', inflections: ['nîpin', 'ê-nîpihk']},
      {pos: 'NAD', lemma: 'nôhkom', inflections: ['kôhkom', 'ohkoma']},
      {pos: 'NID', lemma: 'mîpit', inflections: ['nîpit', 'kîpit', 'wîpit']},
      {pos: 'NA', lemma: 'minôs', inflections: ['minôsak', 'minôsa']},
      {pos: 'NI', lemma: 'nipiy', inflections: ['nipîhk', 'ninipiy', 'kinipiy']},
    ]

    // Create test cases for each word above
    for (let {pos, lemma, inflections} of testCases) {
      it(`should display the paradigm for an ${pos} word`, () => {
        cy.visitSearch(lemma)
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
      cy.visitSearch('minôsis')
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
