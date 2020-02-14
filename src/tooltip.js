// adapted from poppers.js tutorial https://popper.js.org/docs/v2/tutorial/
import {createPopper} from '@popperjs/core/dist/esm/popper';


let popperInstance = null

function create(icon, popup) {
  popperInstance = createPopper(icon.get(0), popup.get(0), {
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
 * @param icon {jQuery}: icon that triggers the popup on hover/click/focus
 * @param popup {jQuery}: the popup that shows up
 */
export function createTooltip(icon, popup) {
  showEvents.forEach(event => {
    icon.on(event, () => {
      popup.attr('data-show', '')
      create(icon, popup)
    })
  })

  hideEvents.forEach(event => {
    icon.on(event, () => {
      popup.removeAttr('data-show')
      destroy()
    })
  })
}

