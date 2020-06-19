describe(' I want to search for a Cree word and see its inflectional paradigm', () => {
  // Test at least one word from each word class:
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


describe('paradigms are visitable from link', () => {
  const lemmaText = 'niska'
  it('shows basic paradigm', () => {
    cy.visitLemma(lemmaText, {'analysis': 'niska+N+A+Sg'})
    // Smaller/Lesser/Younger is an exclusive user friendly tag for BASIC paradigms
    cy.get('[data-cy=paradigm]').contains('Smaller/Lesser/Younger')
  })

  it('shows full paradigm', () => {
    cy.visitLemma(lemmaText, {'analysis': 'niska+N+A+Sg', 'paradigm-size': 'FULL'})
    // his/her/their is an exclusive user friendly tag for FULL paradigms
    cy.get('[data-cy=paradigm]').contains('his/her/their')
  })

  it('shows linguistic paradigm', () => {
    cy.visitLemma(lemmaText, {'analysis': 'niska+N+A+Sg', 'paradigm-size': 'LINGUISTIC'})
    // DIMINUTIVE is an exclusive linguistic term for FULL paradigms
    cy.get('[data-cy=paradigm]').contains('DIMINUTIVE')
  })
}
)


describe.only('paradigms can e toggled by the show more/less button', () => {
  it('shows basic, full, linguistic, and basic paradigm in sequence', () => {
    cy.visitLemma('nipâw')
    // "Something is happening now" is an exclusive user friendly tag for BASIC paradigms
    cy.get('[data-cy=paradigm]').contains('Something is happening now')

    cy.get('[data-cy=paradigm-toggle-button]').click()
    // s/he/they is an exclusive user friendly tag for FULL paradigms
    cy.get('[data-cy=paradigm]').contains('s/he/they')
    // somehow I have to add these cy.wait for the test to pass, fetch request a bit slow?
    cy.wait(100)
    cy.get('[data-cy=paradigm-toggle-button]').click()
    // 2p is an exclusive linguistic term for LINGUISTIC paradigms
    cy.wait(100)
    cy.get('[data-cy=paradigm]').contains('2p')

    cy.get('[data-cy=paradigm-toggle-button]').click()
    cy.wait(100)
    // now are we back to basic?
    cy.get('[data-cy=paradigm]').contains('Something is happening now')

  })
}
)