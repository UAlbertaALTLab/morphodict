/**
 * General tests about the website's behaviour as a regular website.
 */
context('The About page', function () {
  describe('Visiting any page', () => {
    it('should have a link to the about page in the footer', () => {
      cy.visit('/')
      cy.get('footer')
        .contains('a', 'About')
    })

  })

  beforeEach(function () {
    cy.visit('/about')
  })

  describe('Visiting the about page', () => {
    it('should have a few required sections', () => {
      cy.get('main').contains('h2', /Source Materials/i)
      cy.get('main').contains('h2', 'Credits')
      cy.get('main').contains('h2', /Contact Us/i)
    })

    it('should have sponsers logos')
  })
})
