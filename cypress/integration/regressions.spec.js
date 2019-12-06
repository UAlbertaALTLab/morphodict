context('Regressions', () => {
  /**
   * Cypress does not URL-encode non-ASCII components in URLs automatically,
   * but many of our test cases become dramatically easier to write if this
   * magic is done for us. So, test that this is the case!
   */
  it('should handle a non-ASCII letter in the URL properly', () => {
    cy.visit('/search/acâhkos')

    cy.get('[data-cy=search-results]')
      .should('contain', 'atâhk')
  })

  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/158
  it('should basic relevant English results', () => {
    cy.visit('/search/see')
    cy.get('[data-cy=search-results]')
      .should('contain', 'wâpiw')
      .and('contain', 'wâpahtam')
      .and('contain', 'wâpamêw')

    cy.visit('/search/eat')
    cy.get('[data-cy=search-results]')
      .should('contain', 'mîcisow')
      .and('contain', 'mîciw')
      .and('contain', 'mowêw')

    cy.visit('/search/sleep')
    cy.get('[data-cy=search-results]')
      .should('contain', 'nipâw')
  })

  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/161
  it('should show preverbs', () => {
    cy.visit('/search/ati')
    cy.get('[data-cy=search-results]')
      .should('contain', 'ati-')

    cy.visit('/search/ati-')
    cy.get('[data-cy=search-results]')
      .should('contain', 'ati-')

    cy.visit('/search/poni')
    cy.get('[data-cy=search-results]')
      .should('contain', 'poni')

    cy.visit('/search/nitawi')
    cy.get('[data-cy=search-results]')
      .should('contain', 'nitawi-')

    cy.visit('/search/pe')
    cy.get('[data-cy=search-results]')
      .should('contain', 'pe')

  })

  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/160
  it('should show results for pronouns', () => {
    cy.visit('/search/oma')
    cy.get('[data-cy=search-results]')
      .should('contain', 'ôma')

    cy.visit('/search/awa')
    cy.get('[data-cy=search-results]')
      .should('contain', 'awa')

    cy.visit('/search/niya')
    cy.get('[data-cy=search-results]')
      .should('contain', 'niya')
  })

  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/176
  it.skip('should show results for lexicalized diminutive forms', () => {
    // todo: enable this after lemma resolution process is fixed. See #176
    cy.visit('/search/acâhkos')
    cy.get('[data-cy=search-results]')
      .should('contain', 'atâhk')
  })
})
