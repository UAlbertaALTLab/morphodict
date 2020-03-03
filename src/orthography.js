/**
 * Orthography switching.
 */

const AVAILABLE_ORTHOGRAPHIES = new Set(['Cans', 'Latn', 'LatnXMacron'])

/**
 * Listen to ALL clicks on the page, and change orthography for elements that
 * have the data-orth-switch.
 */
export function registerEventListener() {
  document.body.addEventListener('click', function (evt) {
    let target = evt.target
    if (!target.dataset.orthSwitch) {
      return
    }

    let orth = target.value
    changeOrth(orth)
  })
}

/**
 * Changes the orthography of EVERYTHING on the page.
 */
export function changeOrth (which) {
  if (!AVAILABLE_ORTHOGRAPHIES.has(which)) {
    throw new Error(`tried to switch to unknown orthography: ${which}`)
  }

  let elements = document.querySelectorAll('[data-orth]')
  let attr = `orth${which}`
  for (let el of elements) {
    let newText = el.dataset[attr]
    if (newText) {
      el.innerText = newText
    }
  }
}
