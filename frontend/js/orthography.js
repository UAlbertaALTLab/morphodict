/**
 * @file
 * Orthography switching.
 */

const AVAILABLE_ORTHOGRAPHIES = new Set([
  "Cans",
  "Latn",
  "Latn-x-macron",
  "Latn-y",
  "Latn-x-macron-y",
  "CMRO",
]);

/**
 * This **must** be set in order to update the orthography cookie on the
 * server-side.
 */
let djangoCSRFToken = null;

/**
 * Listen to ALL clicks on the page, and change orthography for elements that
 * have the data-orth-switch.
 */
export function registerEventListener(csrfToken) {
  // Try to handle a click on ANYTHING.
  // This way, if new elements appear on the page dynamically, we never
  // need to register new event listeners: this one will work for all of them.
  document.body.addEventListener("click", handleClickSwitchOrthography);
  djangoCSRFToken = csrfToken;
}

/**
 * Changes the orthography of EVERYTHING on the page.
 */
export function changeOrth(which) {
  if (!AVAILABLE_ORTHOGRAPHIES.has(which)) {
    throw new Error(`tried to switch to unknown orthography: ${which}`);
  }

  let elements = document.querySelectorAll("[data-orth]");
  let attr = `data-orth-${which}`;
  for (let el of elements) {
    let newText = el.getAttribute(attr);
    if (newText) {
      el.innerText = newText;
    }
  }
}

/**
 * Switches orthography and updates the UI.
 */
function handleClickSwitchOrthography(evt) {
  let target = findClosestOrthographySwitch(evt.target);
  // Determine that this is a orthography changing button.
  if (!target) {
    return;
  }

  // target is a <button data-orth-swith="ORTHOGRAPHY">
  let orth = target.value;
  changeOrth(orth);
  updateUI(target);
  updateCookies(orth);
}

function findClosestOrthographySwitch(el) {
  return el.closest("[data-orth-switch]");
}

/**
 * Updates the UI following an orthography switch.
 * Assumes the following HTML:
 *
 *  <details>
 *    <summary>CURRENT ORTHOGRAPHY</summary>
 *    <ul>
 *      <li class="menu-choice menu-choice--selected">
 *        <button data-orth-switch value="ORTH">CURRENT ORTHOGRAPHY</button>
 *      </li>
 *      <li class="menu-choice">
 *        <button data-orth-switch value="ORTH">DIFFERENT ORTHOGRAPHY</button>
 *      </li>
 *    </ul>
 *  </details>
 */
function updateUI(button) {
  // Climb up the DOM tree to find the <details> and its <summary> that contains the title.
  let detailsElement = button.closest("details");
  if (!detailsElement) {
    // there absolutely should be a <de
    throw new Error("Could not find relevant <details> element!");
  }

  closeMenu();

  // Clear the selected class from all options
  for (let el of detailsElement.querySelectorAll("[data-orth-switch]")) {
    let li = el.closest(".menu-choice");
    li.classList.remove("menu-choice--selected");
  }
  button.closest(".menu-choice").classList.add("menu-choice--selected");

  function closeMenu() {
    detailsElement.open = false;
  }
}

/**
 * Sends a request to the server to update the orthography cookie.
 * This ensures future requests will be sent with the current orthography.
 */
function updateCookies(orth) {
  if (djangoCSRFToken == null) {
    throw new Error("djangoCSRFToken is unset!");
  }

  let changeOrthURL = window.Urls["morphodict.orthography:change-orthography"]();
  fetch(changeOrthURL, {
    method: "POST",
    body: new URLSearchParams({
      orth: orth,
    }),
    headers: new Headers({
      "X-CSRFToken": djangoCSRFToken,
    }),
  });
}
