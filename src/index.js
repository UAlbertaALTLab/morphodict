/* global Urls:readable */

// "Urls" is a magic variable that allows use to reverse urls in javascript
// See https://github.com/ierror/django-js-reverse

let $ = require('jquery')

/**
 * use ajax to load search results
 *
 * @param {jQuery} $input
 */
function load_results($input) {

  let text = $input.val()
  let instruction = $('#introduction-text')
  // let loading_cards = document.getElementsByClassName('title-row-container loading-title-row')

  if (text !== '') {
    // remove existing boxes

    window.history.replaceState(text, '', Urls['cree-dictionary-index-with-word'](text))

    instruction.hide()

    // show loading cards

    let xhttp = new XMLHttpRequest()
    xhttp.onreadystatechange = function () {
      if (this.readyState === 4 && this.status === 200) {
        // user input may have changed during the request
        const inputNow = $input.val()
        if (inputNow === text) { // hasn't changed
          // remove loading cards

        }
      }
    }
    xhttp.open('GET', Urls['cree-dictionary-search-api'](text), true)
    xhttp.send()


  } else {
    window.history.replaceState(text, '', Urls['cree-dictionary-index']())
    instruction.show()
    //  remove loading cards if any
  }
}

// document.ready is deprecated, this is the shorthand
$(() => {

  let input = $('#search')
  load_results(input)

  input.on('input', () => {
    load_results(input)
  })


})