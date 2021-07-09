/**
 * How long the toast should stay on the screen by default.
 */
const TOAST_DURATION = 1000;

/**
 * Initialize the global toast element.
 *
 * @param {HTMLDialogElement} element
 */
export function setGlobalElement(el) {
  return (_toast = new Toast(el));
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
    this._classList.add("toast--hidden");
  }

  get _classList() {
    return this._el.classList;
  }

  get _textNode() {
    return this._el.querySelector(".toast__message");
  }

  showSuccess(message) {
    this._setMessage(message);
    this._setCSSModifier("toast--success");
    this._show();
  }

  showFailure(message) {
    this._setMessage(message);
    this._setCSSModifier("toast--failure");
    this._show();
  }

  _setMessage(message) {
    this._textNode.textContent = message;
    /* Makes screen readers speak the message, only after they're done
     * speaking what they are currently reading: */
    this._el.setAttribute("aria-live", "polite");
  }

  _clearMessage() {
    this._textNode.textContent = "";
    this._el.setAttribute("aria-live", "off");
  }

  _setCSSModifier(newClass) {
    this._classList.remove("toast--success", "toast--failure");
    this._classList.add(newClass);
  }

  _show() {
    if (this._timer) {
      clearTimeout(this._timer);
    }

    this._timer = setTimeout(() => void this._hide(), TOAST_DURATION);
    this._el.show();
    this._classList.remove("toast--hidden");
  }

  _hide() {
    this._classList.add("toast--hidden");

    const closeDialog = () => {
      this._el.close();
      this._clearMessage();
    };

    this._el.addEventListener("transitionend", closeDialog, { once: true });
  }
}

let _toast = null;

function globalToastOrThrow() {
  if (_toast === null) {
    throw new Error(
      "The toast has not been configured! Did you call toast.setGlobalElement()?"
    );
  }
  return _toast;
}
