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
  const ERROR_CLASS = 'search-progress--error'
  const LOADING_CLASS = 'search-progress--loading'

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

    let xhttp = new XMLHttpRequest()

    xhttp.onloadstart = function () {
      // Show the loading indicator:
      indicateLoading()
    }

    xhttp.onload = function () {
      if (xhttp.status === 200) {
        // user input may have changed during the request
        const inputNow = $input.val()
        if (inputNow === text) { // hasn't changed
          // Remove loading cards
          indicateLoadedSuccessfully()

          $searchResultList.html(xhttp.responseText)
        }
      } else {
        indicateLoadingFailure()
      }
    }

    xhttp.onerror = function () {
    }

    xhttp.open('GET', Urls['cree-dictionary-search-results'](text), true)
    xhttp.send()
  }

  function goToHomePage() {
    window.history.replaceState(text, '', Urls['cree-dictionary-index']())

    instruction.show()

    hideLoadingIndicator()
    $searchResultList.empty()
  }

  function indicateLoading() {
    // Make a 10% progress bar. We actually don't know how much
    // there is left, but make it seem like it's thinking about it!
    progress.max = 100
    progress.value = 10
    progress.classList.remove(ERROR_CLASS)
    progress.classList.add(LOADING_CLASS)
  }

  function indicateLoadedSuccessfully() {
    progress.value = 100
    hideLoadingIndicator()
  }

  function indicateLoadingFailure() {
    // makes the loading state "indeterminate", like it's loading forever.
    progress.removeAttribute('value')
    progress.classList.add(ERROR_CLASS)
  }

  function hideLoadingIndicator() {
    progress.classList.remove(LOADING_CLASS, ERROR_CLASS)
  }
}

/**
 * Change tab title according to user input in the search bar
 *
 * @param inputVal {string}
 */
function changeTitleByInput(inputVal) {
  let defaultTitle = 'itwêwina: the online Cree dictionary'
  document.title = inputVal ? inputVal + ' — ' + defaultTitle : defaultTitle
}


// document.ready is deprecated, this is the shorthand
$(() => {
  let $input = $('#search')
  loadResults($input)
  changeTitleByInput($input.val())

  $input.on('input', () => {
    loadResults($input)
    changeTitleByInput($input.val())
  })
})
