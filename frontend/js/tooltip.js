// adapted from poppers.js tutorial https://popper.js.org/docs/v2/tutorial/
import { createPopper } from "@popperjs/core/dist/esm/popper";

const showEvents = ["mouseenter", "focus"];
const hideEvents = ["mouseleave", "blur"];
const permanenceChangeEvents = ["click"];
const outsidePopupCloseEvents = ["click"];

/**
 * prepare the popup and the icon. Attach relevant handlers
 *
 * @param icon {Element}: icon that triggers the popup on hover/click/focus
 * @param popup {Element}: the popup that shows up
 */
export function createTooltip(icon, popup) {
  let permanent = false;
  let popperInstance = null;

  /**
   * @param {Element} icon
   * @param {Element} popup
   */
  function create(icon, popup) {
    popperInstance = createPopper(icon, popup, {
      modifiers: [
        {
          name: "offset",
          options: {
            offset: [0, 8],
          },
        },
      ],
    });
  }

  function destroy() {
    if (popperInstance) {
      popperInstance.destroy();
      popperInstance = null;
    }
  }

  function show() {
    if (!popperInstance) {
      popup.setAttribute("data-show", "");
      create(icon, popup);
    }
  }
  function hide() {
    if (!permanent && popperInstance) {
      popup.removeAttribute("data-show");
      destroy();
    }
  }
  for (let event of showEvents) {
    icon.addEventListener(event, show);
  }

  for (let event of hideEvents) {
    icon.addEventListener(event, hide);
  }

  for (let event of permanenceChangeEvents) {
    icon.addEventListener(event, () => {
      permanent = !permanent;
      if (!permanent) {
        hide();
      } else {
        show();
      }
    });
  }

  for (let event of outsidePopupCloseEvents) {
    document.addEventListener(event, (event) => {
      if (!popup.contains(event.target) && !icon.contains(event.target)) {
        permanent = false;
        hide();
      }
    });
  }
}
