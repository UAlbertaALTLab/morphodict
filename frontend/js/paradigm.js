/**
 * Set up any page that has the #paradigm element with its size controls.
 */
export function setupParadigm() {
  setupParadigmSizeToggleButton(null)
}

// TODO: the backend should SOLELY maintain this list:
const ALL_PARADIGM_SIZES = ['BASIC', 'FULL', 'LINGUISTIC']

/**
 * attach handlers to the "show more/less" button. So that it:
 *
 *  - loads a more detailed paradigm when clicked or do nothing and report to console if the request for the paradigm errors
 *  - changes its text to "show less" when the paradigm has the largest size
 *    and shows the smallest paradigm when clicked
 *  - prepare the new "show more/less" button to do these 3
 */
function setupParadigmSizeToggleButton(currentParadigmSize) {
  const toggleButton = document.querySelector('.js-paradigm-size-button')

  if (!toggleButton) {
    // There's nothing to toggle, hence nothing to setup. Done!
    return
  }

  // `lemmaId` should be embedded by Django into the template.
  // It's present when the current page is lemma detail/paradigm page
  const lemmaId = readDjangoJsonScript('lemma-id')
  // `paradigmSize` is also rendered by a Django template
  // And it can changed dynamically by JavaScript when the script loads different sized paradigms
  let paradigmSize = currentParadigmSize || readDjangoJsonScript('paradigm-size')

  const nextParadigmSize = getNextParadigmSize(paradigmSize)

  toggleButton.addEventListener('click', () => {
    displayButtonAsLoading(toggleButton)

    fetch(window.Urls['cree-dictionary-paradigm-detail']() + `?lemma-id=${lemmaId}&paradigm-size=${nextParadigmSize}`).then(r => {
      if (r.ok) {
        return r.text()
      } else {
        // TODO: show error on the loading component
        throw new Error(`${r.status} ${r.statusText} when loading paradigm: ${r.text()}`)
      }
    }).then(
      text => {
        const newParadigm = document.createRange().createContextualFragment(text)

        // TODO: the backend should SOLELY maintain this:
        if (mostDetailedParadigmSizeIsSelected()) {
          setParadigmSizeToggleButtonText('-', 'show less')
        } else {
          setParadigmSizeToggleButtonText('+', 'show more')
        }

        const paradigmContainer = document.getElementById('paradigm')
        paradigmContainer.querySelector('.js-replaceable-paradigm').replaceWith(newParadigm)

        paradigmSize = nextParadigmSize
        setupParadigmSizeToggleButton(paradigmSize)
        updateCurrentURLWithParadigmSize()

        function setParadigmSizeToggleButtonText(symbol, text) {
          newParadigm.querySelector('.js-button-text').textContent = text
          newParadigm.querySelector('.js-plus-minus').textContent = symbol
        }
      }
    ).catch((err) => {
      displayButtonAsError(toggleButton)
      console.error(err)
    })
  })

  // TODO: the backend should know this:
  function mostDetailedParadigmSizeIsSelected() {
    return ALL_PARADIGM_SIZES.indexOf(nextParadigmSize) === ALL_PARADIGM_SIZES.length - 1
  }

  function updateCurrentURLWithParadigmSize() {
    window.history.replaceState({}, document.title, updateQueryParam('paradigm-size', nextParadigmSize))
  }
}

/**
 * Make the button look like it's loading.
 */
function displayButtonAsLoading(toggleButton) {
  toggleButton.classList.add('paradigm__size-toggle-button--loading')
}

/**
 * Make the button look like something went wrong.
 */
function displayButtonAsError(toggleButton) {
  toggleButton.classList.remove('paradigm__size-toggle-button--loading')
  // TODO: should have an error state for the toggle button!
}


/**
 * cycles between BASIC, FULL, LINGUISTIC
 *
 * @param {String} size
 * @return {String}
 */
function getNextParadigmSize(size) {
  return ALL_PARADIGM_SIZES[(ALL_PARADIGM_SIZES.indexOf(size) + 1) % ALL_PARADIGM_SIZES.length]
}

///////////////////////////// Internal functions /////////////////////////////

/**
 * Read JSOn data produced by Django's `json_script` filter during HTML template generation
 */
function readDjangoJsonScript(id) {
  const jsonScriptElement = document.getElementById(id)
  if (jsonScriptElement) {
    return JSON.parse(jsonScriptElement.textContent)
  } else {
    return undefined
  }
}

/**
 * https://stackoverflow.com/a/11654596
 * get the current url and update a query param
 *
 * @param {String} key
 * @param {String} value
 * @returns {String}
 */
function updateQueryParam(key, value) {
  let url = window.location.href
  let re = new RegExp('([?&])' + key + '=.*?(&|#|$)(.*)', 'gi'),
    hash

  if (re.test(url)) {
    if (typeof value !== 'undefined' && value !== null) {
      return url.replace(re, '$1' + key + '=' + value + '$2$3')
    } else {
      hash = url.split('#')
      url = hash[0].replace(re, '$1$3').replace(/([&?])$/, '')
      if (typeof hash[1] !== 'undefined' && hash[1] !== null) {
        url += '#' + hash[1]
      }
      return url
    }
  } else {
    if (typeof value !== 'undefined' && value !== null) {
      const separator = url.indexOf('?') !== -1 ? '&' : '?'
      hash = url.split('#')
      url = hash[0] + separator + key + '=' + value
      if (typeof hash[1] !== 'undefined' && hash[1] !== null) {
        url += '#' + hash[1]
      }
      return url
    } else {
      return url
    }
  }
}
