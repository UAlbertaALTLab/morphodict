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

  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/147
  it('should allow space characters in exact strings', () => {
    cy.visit('/search/acâhkos kâ-osôsit')
    cy.get('[data-cy=search-results]')
      .should('contain', 'acâhkos kâ-osôsit')

    cy.visit('/search/acâhkosa kâ-otakohpit')
    cy.get('[data-cy=search-results]')
      .should('contain', 'acâhkosa kâ-otakohpit')
  })

  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/147
  it('should allow space characters in spell-relaxed results', () => {
    cy.visit('/search/niki nitawi kiskinwahamakosin')
    cy.get('[data-cy=search-results]')
      .should('contain', 'kiskinwahamâkosiw')

    cy.visit('/search/ka ki awasisiwiyan')
    cy.get('[data-cy=search-results]')
      .should('contain', 'awâsisîwiw')

    cy.visit('/search/na nipat')
    cy.get('[data-cy=search-results]')
      .should('contain', 'nipâw')
  })


  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/158
  it('should display relevant English results', () => {
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
  it('should show results for lexicalized diminutive forms', () => {
    cy.visit('/search/acâhkos')
    cy.get('[data-cy=search-results]')
      .should('contain', 'atâhk')
  })
  
  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/176
  describe('should show idiomatic lemmas', ()=>{
    it('The Cree word ayiwinis should give you ayiwinisa as lemma', () => {
      cy.visit('/search/ayiwinis')
      cy.get('[data-cy=search-results]')
        .should('contain', 'ayiwinisa')
    })
  })
  
  // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/176
  describe('should show at least two lemmas for lexicalized diminutive forms', ()=>{
    it('should show atâhk and acâhkos for acâhkos', () => {
      cy.visit('/search/acâhkos')
      cy.get('[data-cy=search-results]')
        .should('contain', 'atâhk')
        .and('contain', 'acâhkos')
    })

    // see: https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/176#issuecomment-563336151
    // Note: It's in dispute whether minôsis should be treated as a diminutive form of minôs
    // todo: enable this test if fst recognized minôsis as diminutive minôs
    it.skip('should show minôs and minôsis for minôsis', () => {
      cy.visit('/search/minôsis')
      cy.get('[data-cy=search-results]')
        .should('contain', 'minôsis')
        .and('contain', 'minôs')
    }
    )
  })
    
  it('The Cree word ayiwinis should give you ayiwinisa as lemma', () => {
    cy.visit('/search/ayiwinis')
    cy.get('[data-cy=search-results]')
      .should('contain', 'ayiwinisa')
  })
  

})
