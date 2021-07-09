/**
 * How long the toast should stay on the screen by default.
 */
const TOAST_DURATION = 3000;

let _toast = null;

/**
 * Initialize the global toast element.
 *
 * @param {HTMLDialogElement} element
 */
export function setGlobalElement(el) {
  _toast = new Toast(el);
}

/**
 * Show a message that something succeeded.
 */
export function showSuccess(message) {
  return globalToastOrThrow().showSuccess(message);
}

/**
 * Show a message that something failed.
 */
export function showFailure(message) {
  return globalToastOrThrow().showFailure(message);
}

const ALL_EXPECTED_MODIFIERS = ["toast--success", "toast--failure"];

/**
 * Toast component.
 *
 * A toast is a small, minimally intrusive notifcation.
 *
 * See: https://cultureamp.design/components/toast-notification/
 *
 * (At what point do you consider using a frontend UI framework? :S)
 */
class Toast {
  constructor(element) {
    /* == null matches **both** null and undefined. */
    if (element == null || !(element instanceof HTMLDialogElement)) {
      throw new TypeError("must provide a valid <dialog> element");
    }

    this._el = element;
    this._timer = null;

    this._el.close();
    this._classList.add("toast--off-screen");
    /* Makes screen readers speak the message, only after they're done
     * speaking what they are currently reading: */
    this._el.setAttribute("aria-live", "polite");
  }

  /**
   * Show a message that something succeeded.
   */
  showSuccess(message) {
    this._setMessage(message);
    this._setCSSModifier("toast--success");
    this._show();
  }

  /**
   * Show a message that something failed.
   */
  showFailure(message) {
    this._setMessage(message);
    this._setCSSModifier("toast--failure");
    this._show();
  }

  get _classList() {
    return this._el.classList;
  }

  get _textNode() {
    return this._el.querySelector(".toast__message");
  }

  _setMessage(message) {
    this._textNode.textContent = message;
  }

  _clearMessage() {
    this._textNode.textContent = "";
  }

  _setCSSModifier(modifier) {
    this._classList.remove(...ALL_EXPECTED_MODIFIERS);
    this._classList.add(modifier);
  }

  _show() {
    if (this._timer != null) {
      clearTimeout(this._timer);
    }

    this._timer = setTimeout(() => void this._hide(), TOAST_DURATION);
    this._el.show();
    this._classList.remove("toast--off-screen");
  }

  _hide() {
    this._classList.add("toast--off-screen");
    this._timer = null;

    const closeDialog = () => {
      this._el.close();
      this._clearMessage();
    };

    /* Wait until the CSS animation is finished to actually close the dialog. */
    this._el.addEventListener("transitionend", closeDialog, { once: true });
  }
}

function globalToastOrThrow() {
  if (_toast === null) {
    throw new Error(
      "The toast has not been configured! Did you call toast.setGlobalElement()?"
    );
  }
  return _toast;
}
