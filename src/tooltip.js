// adapted from poppers.js tutorial https://popper.js.org/docs/v2/tutorial/
import {createPopper} from '@popperjs/core/dist/esm/popper'

import $ from 'jquery'

let popperInstance = null

/**
 * @param {Element} icon
 * @param {Element} popup
 */
function create(icon, popup) {
  popperInstance = createPopper(icon, popup, {
    modifiers: [
      {
        name: 'offset',
        options: {
          offset: [0, 8],
        },
      },
    ],
  })
}

function destroy() {
  if (popperInstance) {
    popperInstance.destroy()
    popperInstance = null
  }
}

const showEvents = ['mouseenter', 'focus']
const hideEvents = ['mouseleave', 'blur']

/**
 * prepare the popup and the icon. Attach relevant handlers
 *
 * @param icon {Element}: icon that triggers the popup on hover/click/focus
 * @param popup {Element}: the popup that shows up
 */
export function createTooltip(icon, popup) {
  showEvents.forEach(event => {
    $(icon).on(event, () => {
      popup.setAttribute('data-show', '')
      create(icon, popup)
    })
  })

  hideEvents.forEach(event => {
    $(icon).on(event, () => {
      popup.removeAttribute('data-show')
      destroy()
    })
  })
}
