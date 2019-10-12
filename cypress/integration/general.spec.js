/**
 * General tests about the website's behaviour as a regular website.
 */
context('General', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  describe('Visiting the home page', () => {
    it('should say “itwêwina” in the header', () => {
      cy.get('h1')
        .should('be.visible')
        .should('contain', 'itwêwina')
    })

    it('should greet the users in the content', () => {
      cy.get('main')
        .contains('h1, h2', /\bt[âā]n[i']?si\b/)
        .should('be.visible')
    })
  })
})
