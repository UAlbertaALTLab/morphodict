context('Regressions', () => {
  /**
   * Cypress does not URL-encode non-ASCII components in URLs automatically,
   * but many of our test cases become dramatically easier to write if this
   * magic is done for us. So, test that this is the case!
   */
  it('should handle a non-ASCII letter in the URL properly', () => {
    cy.visitSearch('acâhkos')

    cy.get('[data-cy=search-results]')
      .should('contain', 'atâhk')
  })

  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/147
  it('should allow space characters in exact strings', () => {
    cy.visitSearch('acâhkos kâ-osôsit')
    cy.get('[data-cy=search-results]')
      .should('contain', 'acâhkos kâ-osôsit')

    cy.visitSearch('acâhkosa kâ-otakohpit')
    cy.get('[data-cy=search-results]')
      .should('contain', 'acâhkosa kâ-otakohpit')
  })

  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/147
  it('should allow space characters in spell-relaxed results', () => {
    cy.visitSearch('niki nitawi kiskinwahamakosin')
    cy.get('[data-cy=search-results]')
      .should('contain', 'kiskinwahamâkosiw')

    cy.visitSearch('ka ki awasisiwiyan')
    cy.get('[data-cy=search-results]')
      .should('contain', 'awâsisîwiw')

    cy.visitSearch('na nipat')
    cy.get('[data-cy=search-results]')
      .should('contain', 'nipâw')
  })


  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/158
  it('should display relevant English results', () => {
    cy.visitSearch('see')
    cy.get('[data-cy=search-results]')
      .should('contain', 'wâpiw')
      .and('contain', 'wâpahtam')
      .and('contain', 'wâpamêw')

    cy.visitSearch('eat')
    cy.get('[data-cy=search-results]')
      .should('contain', 'mîcisow')
      .and('contain', 'mîciw')
      .and('contain', 'mowêw')

    cy.visitSearch('sleep')
    cy.get('[data-cy=search-results]')
      .should('contain', 'nipâw')
  })

  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/161
  it('should show preverbs', () => {
    cy.visitSearch('ati')
    cy.get('[data-cy=search-results]')
      .should('contain', 'ati-')

    cy.visitSearch('ati-')
    cy.get('[data-cy=search-results]')
      .should('contain', 'ati-')

    cy.visitSearch('nitawi')
    cy.get('[data-cy=search-results]')
      .should('contain', 'nitawi-')

    cy.visitSearch('pe')
    cy.get('[data-cy=search-results]')
      .should('contain', 'pê-')

  })

  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/160
  it('should show results for pronouns', () => {
    cy.visitSearch('oma')
    cy.get('[data-cy=search-results]')
      .should('contain', 'ôma')

    cy.visitSearch('awa')
    cy.get('[data-cy=search-results]')
      .should('contain', 'awa')

    cy.visitSearch('niya')
    cy.get('[data-cy=search-results]')
      .should('contain', 'niya')
  })

  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/176
  it('should show results for lexicalized diminutive forms', () => {
    cy.visitSearch('acâhkos')
    cy.get('[data-cy=search-results]')
      .should('contain', 'atâhk')
  })


  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/176
  describe('should show at least two lemmas for lexicalized diminutive forms', () => {
    it('should show atâhk and acâhkos for acâhkos', () => {
      cy.visitSearch('acâhkos')
      cy.get('[data-cy=search-results]')
        .should('contain', 'atâhk')
        .and('contain', 'acâhkos')
    })

    // see: https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/176#issuecomment-563336151
    // Note: It's in dispute whether minôsis should be treated as a diminutive form of minôs
    // todo: enable this test if fst recognized minôsis as diminutive minôs
    it.skip('should show minôs and minôsis for minôsis', () => {
      cy.visitSearch('minôsis')
      cy.get('[data-cy=search-results]')
        .should('contain', 'minôsis')
        .and('contain', 'minôs')
    }
    )
  })


  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/181
  it('should just show two meanings for the lemma nipâw', () => {
    cy.visitSearch('nipâw')
    cy.get('[data-cy=search-results]').first()
      .find('[data-cy=lemma-meaning]').should('have.length', 2)
  })


  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/181
  it('should show the NRC logo', () => {
    cy.visit('/about')
    cy.get('[href^="https://nrc.canada.ca/en/research-development/research-collaboration/programs/canadian-indigenous-languages-technology-project"] > img')
      .should('be.visible')
      .invoke('attr', 'src')
      .should('match', /[.]svg$/)
  })

  it('should have the search bar appear wide on desktop', () => {
    let minimumWidth
    const factor = 0.60  // it should be at least 60% the size of the viewport.
    cy.viewport('macbook-13')  // a small laptop size
    cy.visit('/')

    // Get the viewport width first...
    cy.window()
      .then((win) => {
        let viewportWidth = Cypress.$(win).width()
        minimumWidth = viewportWidth * factor
      })
      .then(() => {
        cy.get('[data-cy=search]')
          .invoke('width')
          .should('be.greaterThan', minimumWidth)
      })
  })

  it('should show 3>1,2 rather than 3\', 3 in the VTA layout', function () {
    // Go to a VTA word:
    cy.visitSearch('wâpamêw')
    cy.contains('a', 'wâpamêw')
      .click()

    // N.B.: This test will fail if the word changes. ¯\_(ツ)_/¯
    cy.contains('th', 's/he → him/her/them (further)') // 3Sg -> 4 (lemma)
    cy.contains('th', 's/he → me')                  // 3Sg -> 1Sg
    cy.contains('th', 's/he → you (one)')           // 3Sg -> 2Sg
    cy.contains('th', 's/he/they (further) → him/her') // 4 -> 3
  })

  /**
   * Ensure search can be initiated from about page.
   *
   * See: https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/280
   */
  it('should search from the about page', function () {
    cy.visit('/about')
    cy.get('[data-cy="search"]')
      .type('acâhkos')

    cy.url()
      .should('contain', '/search')
    cy.get('[data-cy=search-results]')
      .should('contain', 'atâhk')
  })


  /**
   * Ensure English names with capitalization gets matches
   *
   * See: https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/343
   */
  it('should present results when one searches with capitalized English names', function () {
    cy.visitSearch('Cree')
    cy.get('[data-cy=search-results]').should('be.visible')

    cy.visitSearch('Edmonton')
    cy.get('[data-cy=search-results]').should('be.visible')
  })


  /**
   * Ensure preverbs don't get weird search results
   *
   * See: https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/355
   */
  it('should not present un-related translation for preverbs', function () {
    cy.visitSearch('nitawi-')

    // there should be only one result
    cy.get('[data-cy=search-results]').first()
      .should('contain', 'go and')
  })
})
