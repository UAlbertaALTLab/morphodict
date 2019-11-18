/**
 * General tests about the website's behaviour as a regular website.
 */
context('The About page', function () {
  beforeEach(function () {
    cy.visit('/about')
  })

  describe('Visiting the about page', () => {
    it('should have a link in the footer', () => {
      cy.get('footer')
        .contains('a', 'About')
    })
  })
})
