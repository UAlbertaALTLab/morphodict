context('Word details', () => {
  describe('I want to see the word class and inflectional category for a Cree word', () => {
    // Test at least one word from each word class:
    //
    const testCases = [
      {wc: 'VTA', word: 'mowêw'},
      {wc: 'VAI', word: 'wâpiw'},
      {wc: 'VTI', word: 'mîcisow'},
      {wc: 'VII', word: 'nîpin'},
      {wc: 'NAD', word: 'nôhkom'},
      {wc: 'NID', word: 'mîpit'},
      {wc: 'NA', word: 'minôs'},
      {wc: 'NI', word: 'nipiy'},
      {wc: 'IPC', word: 'ispîhk'},
    ]

    // Create test cases for each word above
    for (let {wc, word} of testCases) {
      it(`should display the word class and inflection class for ${word} (${wc})`, () => {
        cy.visitLemma(word)

        cy.url()
          .should('contain', 'word/')

        // TODO: assert that we can see the word class and inflectional
        // category!
      })
    }
  })
})
