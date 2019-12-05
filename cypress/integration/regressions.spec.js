context('Regressions', () => {
  it('should handle a non-ASCII letter in the URL properly', () => {
    cy.visit('/search/acâhkos')

    cy.get('[data-cy=search-results]')
      .should('contain', 'atâhk')
  })
  // # 158
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

  // # 159
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

  // # 160
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

  it.skip('should show results for lexicalized diminutive forms', () => {
    // todo: enable this after lemma resolution process is fixed. See #176
    cy.visit('/search/acâhkos')
    cy.get('[data-cy=search-results]')
      .should('contain', 'atâhk')
  })
})
