/* global Urls:readable */

// "Urls" is a magic variable that allows use to reverse urls in javascript
// See https://github.com/ierror/django-js-reverse

let $ = require('jquery')

/**
 * use ajax to load search results
 *
 * @param {jQuery} $input
 */
function loadResults($input) {
  let text = $input.val()
  let instruction = $('#introduction-text')
  // let loading_cards = document.getElementsByClassName('title-row-container loading-title-row')

  let $searchResultList = $('#search-result-list').html(this.responseText)

  if (text !== '') {
    issueSearch()
  } else {
    goToHomePage()
  }

  function issueSearch() {
    window.history.replaceState(text, '', Urls['cree-dictionary-index-with-word'](text))

    instruction.hide()
    // todo: show loading cards

    let xhttp = new XMLHttpRequest()
    xhttp.onreadystatechange = function () {
      if (xhttp.readyState === 4 && xhttp.status === 200) {
        // user input may have changed during the request
        const inputNow = $input.val()
        if (inputNow === text) { // hasn't changed
          // todo: remove loading cards

          $searchResultList.html(xhttp.responseText)
        }
      }
    }
    xhttp.open('GET', Urls['cree-dictionary-search-results'](text), true)
    xhttp.send()
  }

  function goToHomePage() {
    window.history.replaceState(text, '', Urls['cree-dictionary-index']())

    instruction.show()

    // todo: remove loading cards if any
    $searchResultList.empty()
  }
}

// document.ready is deprecated, this is the shorthand
$(() => {
  let input = $('#search')
  loadResults(input)

  input.on('input', () => {
    loadResults(input)
  })
})
