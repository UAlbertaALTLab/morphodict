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
  let progress = document.getElementById('loading-indicator')

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
      if (xhttp.readyState === 4) {
        if (xhttp.status === 200) {
          // user input may have changed during the request
          const inputNow = $input.val()
          if (inputNow === text) { // hasn't changed
            // Remove loading cards
            indicateLoadedSuccessfully()

            $searchResultList.html(xhttp.responseText)
          }
        } else if (xhttp.status >= 400) {
          progress.classList.add('search-progress--error')
        }
      }
    }
    xhttp.open('GET', Urls['cree-dictionary-search-results'](text), true)
    xhttp.send()
    // Show the loading indicator:
    indicateLoading()
  }

  function goToHomePage() {
    window.history.replaceState(text, '', Urls['cree-dictionary-index']())

    instruction.show()

    hideLoadingIndicator()
    $searchResultList.empty()
  }

  function indicateLoading() {
    progress.classList.add('search-progress--loading')
  }

  function indicateLoadedSuccessfully() {
    hideLoadingIndicator()
  }

  function hideLoadingIndicator() {
    progress.classList.remove('search-progress--loading')
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
