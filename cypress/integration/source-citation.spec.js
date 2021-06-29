/**
 * Test how citations should work in crkeng (itwêwina Plains Cree
 * dictionary).
 */
describe('Source citations', function () {
  const LEMMA_WITH_MD_AND_CW_CITATIONS = 'mowêw'
  const SOURCES = ['MD', 'CW']
  const CRITICAL_INFORMATION = {
    'MD': 'Maskwacîs Dictionary',
    'CW': 'Cree: Words',
  }

  context('Search page', () => {
    it('should cite on the search page, with a tooltip', () => {
      cy.visitSearch(LEMMA_WITH_MD_AND_CW_CITATIONS)

      for (let sourceAbbreviation of SOURCES) {
        clearFocus()

        searchResult()
          .contains('cite', sourceAbbreviation)
          .first()
          .as('citation')
          .click()

        tooltip()
          .should('be.visible')
          .contains(CRITICAL_INFORMATION[sourceAbbreviation])
      }
    })

    function searchResult() {
      return cy.get('[data-cy=search-result]').first()
    }

    function tooltip() {
      return cy.get('[data-cy=citation-tooltip]')
    }
  })

  context('Details page', () => {
    it('should ...', () => {
      cy.visitLemma(LEMMA_WITH_MD_AND_CW_CITATIONS)
    })
  })

  function clearFocus() {
    cy.get('[data-cy=search]').click().blur()
  }
})
