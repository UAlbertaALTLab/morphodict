// if I click this or visit that, xxx should happen

// corresponding requirements: https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/143
describe('urls for lemma detail page should be handled correctly', ()=>{
  it('should show lemma detail (paradigms) if a unambiguous url is given', function () {

    // Get to the definition/paradigm page for "wâpamêw"
    cy.visit('/word/wâpamêw/')
    cy.get('[data-cy=paradigm]')
      .should('be.visible')
      .and('contain', 'kiwâpamitin')
  })
  it('should redirect to search page if no match is found', function () {

    // poopoo is a fictional word
    cy.visit('/word/poopoo/')
    cy.get('[data-cy=paradigm]')
      .should('not.exist')

    // test if the redirection happens
    cy.location().should(
      (loc)=>{
        expect(loc.pathname).to.eq('/search/poopoo/')
      }
    )


    // wrong constraint pos=N is supplied, nipâw should have pos V
    cy.visit('/word/nipâw', {qs:{'pos':'N'}})
    cy.get('[data-cy=paradigm]')
      .should('not.exist')

    // test if the redirection happens
    cy.location().should(
      (loc)=>{
        expect(loc.pathname).to.eq(`/search/${encodeURIComponent('nipâw')}/`)
      }
    )

  })

  it('should redirect to search page if the lemma_text in /word/lemma_text matches multiple results', function () {

    // pipon is a verb as well as a noun
    cy.visit('/word/pipon/')
    cy.get('[data-cy=paradigm]')
      .should('not.exist')

    // test if the redirection happens
    cy.location().should(
      (loc)=>{
        expect(loc.pathname).to.eq('/search/pipon/')
      }
    )

  })

  it('should add relevant constraints in query params for ambiguous lemmas', function () {

    // pipon is a verb as well as a noun
    cy.visit('/search/pipon/')

    // both results should be present
    cy.get('[data-cy=definition-title] a').first()
      .should('have.attr', 'href')
      .and('eq', '/word/pipon/?pos=N')

    cy.get('[data-cy=definition-title] a').eq(1)
      .should('have.attr', 'href')
      .and('eq', '/word/pipon/?pos=V')

  })


})
