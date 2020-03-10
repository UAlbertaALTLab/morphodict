/* global Urls:readable */
// "Urls" is a magic variable that allows use to reverse urls in javascript
// See https://github.com/ierror/django-js-reverse

import $ from 'jquery'

// Process CSS with PostCSS automatically. See rollup.config.js for more
// details.
import './css/styles.css'
import {createTooltip} from './tooltip'
import {fetchFirstRecordingURL} from './recordings.js'
import * as orthography from './orthography.js'

const ERROR_CLASS = 'search-progress--error'
const LOADING_CLASS = 'search-progress--loading'

const NO_BREAK_SPACE = '\u00A0'

/**
 * Make a 10% progress bar. We actually don't know how much there is left,
 * but make it seem like it's thinking about it!
 */
function indicateLoading() {
  let progress = document.getElementById('loading-indicator')
  progress.max = 100
  progress.value = 10
  progress.classList.remove(ERROR_CLASS)
  progress.classList.add(LOADING_CLASS)
}


function indicateLoadedSuccessfully() {
  let progress = document.getElementById('loading-indicator')
  progress.value = 100
  hideLoadingIndicator()
}

function indicateLoadingFailure() {
  // makes the loading state "indeterminate", like it's loading forever.
  let progress = document.getElementById('loading-indicator')
  progress.removeAttribute('value')
  progress.classList.add(ERROR_CLASS)
}

function hideLoadingIndicator() {
  let progress = document.getElementById('loading-indicator')
  progress.classList.remove(LOADING_CLASS, ERROR_CLASS)
}


/**
 * clean paradigm details
 */
function cleanParadigm() {
  $('#paradigm').remove()
}


function showProse() {
  let prose = $('#prose')
  prose.show()
}

function hideProse() {
  let prose = $('#prose')
  prose.hide()
}

/**
 * find #search-result-list element on the page to attach relevant handlers to the tooltip icons
 */
function prepareTooltips() {
  const $searchResultList = $('#search-result-list')

  // attach handlers for tooltip icon at preverb breakdown
  $searchResultList.find('.definition-title__tooltip-icon').each(function () {
    createTooltip($(this), $(this).next('.tooltip'))
  })

  // attach handlers for tooltip icon at preverb breakdown
  $searchResultList.find('.preverb-breakdown__tooltip-icon').each(function () {
    createTooltip($(this), $(this).next('.tooltip'))
  })
}

/**
 * use xhttp to load search results in place
 *
 * @param {jQuery} $input
 */
function loadResults($input) {
  let userQuery = $input.val()
  let $searchResultList = $('#search-result-list')

  if (userQuery !== '') {
    issueSearch()
  } else {
    goToHomePage()
  }

  function issueSearch() {
    window.history.replaceState(userQuery, document.title, urlForQuery(userQuery))

    hideProse()

    let xhttp = new XMLHttpRequest()

    xhttp.onloadstart = function () {
      // Show the loading indicator:
      indicateLoading()
    }

    xhttp.onload = function () {
      if (xhttp.status === 200) {
        // user input may have changed during the request
        const inputNow = $input.val()
        if (inputNow === userQuery) { // hasn't changed
          // Remove loading cards
          indicateLoadedSuccessfully()
          cleanParadigm()
          $searchResultList.html(xhttp.responseText)
          prepareTooltips()


        } else { // changed. Do nothing
        }
      } else {
        indicateLoadingFailure()
      }
    }

    xhttp.onerror = function () {
      // TODO: we should do something here!
    }
    xhttp.open('GET', Urls['cree-dictionary-search-results'](userQuery), true)
    xhttp.send()
  }

  function goToHomePage() {
    window.history.replaceState(userQuery, document.title, Urls['cree-dictionary-index']())

    showProse()

    hideLoadingIndicator()
    $searchResultList.empty()
  }

  /**
   * Returns a URL that search for the given query.
   *
   * The URL is constructed by using the <form>'s action="" attribute.
   */
  function urlForQuery(userQuery) {
    let form = $input.get(0).closest('form')
    return form.action + `?q=${encodeURIComponent(userQuery)}`
  }
}

/**
 * Change tab title according to user input in the search bar
 *
 * @param inputVal {string}
 */
function changeTitleByInput(inputVal) {
  setSubtitle(inputVal ? '🔎 ' + inputVal : null)
}

function setSubtitle(subtitle) {
  let defaultTitle = 'itwêwina: the online Cree dictionary'
  document.title = subtitle ? `${subtitle} — ${defaultTitle}` : defaultTitle
}

/**
 * Sets up the (rudimentary) audio link on page load.
 */
function setupAudioOnPageLoad() {
  let title = document.getElementById('head')
  if (!title) {
    // Could not find a head on the page.
    return
  }

  // TODO: setup URL from <link rel=""> or something.
  let template = document.getElementById('template:play-button')
  let dataElement = document.getElementById('data:head')
  let wordform = dataElement.value

  fetchFirstRecordingURL(wordform)
    .then(function (recordingURL) {
      let recording = new Audio(recordingURL)
      recording.preload = 'none'

      let fragment = template.content.cloneNode(true)
      // Place "&nbsp;<button>...</button>"
      // at the end of the <h1?
      // TODO: it shouldn't really be **inside** the <h1>...
      let button = fragment.childNodes[0]
      let nbsp = document.createTextNode(NO_BREAK_SPACE)
      title.appendChild(nbsp)
      title.appendChild(button)
      button.addEventListener('click', function () {
        recording.play()
      })
    })
    .catch(e=>{
      // fixme (eddie): now what?
      console.log(e)
    })
}

/**
 * Makes all URL paths relative to '/'.
 * In development, the root path is '/', so nothing changes.
 * On Sapir (as of 2020-03-09), the root path is '/cree-dictionary/'.
 */
function makeRouteRelativeToSlash(route) {
  let baseURL = Urls['cree-dictionary-index']()
  return route.replace(baseURL, '/')
}

$(() => {
  // XXX: HACK! reloads the site when the back button is pressed.
  $(window).on('popstate', function () {
    location.reload()
  })

  let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value
  orthography.registerEventListener(csrfToken)

  // setup search bar
  let $input = $('#search')
  $input.on('input', () => {
    loadResults($input)
    changeTitleByInput($input.val())
  })

  let route = makeRouteRelativeToSlash(window.location.pathname)
  // Tiny router.
  if (route === '/') {
    // Homepage
    setSubtitle(null)
  } else if (route === '/about') {
    // About page
    setSubtitle('About')
  } else if (route === '/search') {
    // Search page
    prepareTooltips()
  } else if (route.match(/^[/]word[/].+/)) {
    // Word detail/paradigm page. This one has the 🔊 button.
    setupAudioOnPageLoad()
  } else {
    throw new Error(`Could not match route: ${route}`)
  }
})
