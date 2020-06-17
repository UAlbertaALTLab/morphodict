/*!
 * Copyright (c) 2020 Eddie Antonio Santos
 *
 * This Source Code Form is subject to the terms of the Mozilla Public License,
 * v. 2.0. If a copy of the MPL was not distributed with this file, You can
 * obtain one at http://mozilla.org/MPL/2.0/.
 */

/**
 * Simplifies interaction with <template> tags.
 *
 * Usage:
 *
 * In the HTML, create a <template> with <slot> elements. Give it an ID:
 *
 *     <template id="template:hello">
 *       <h1> <slot name="salutation">Hello</slot>, <slot name="recipient">World</slot>!</h1>
 *     </template>
 *
 * Once the <template> is in the DOM, instantiate a SimpleTemplate from its ID:
 *
 *       let greeting = SimpleTemplate.fromId('template:hello')
 *
 * Change the text of <slot name="salutation">:
 *
 *       greeting.slot.salutation = 'Goodbye'
 *
 * Change the text of <slot name="recipient">:
 *
 *       greeting.slot.recipient = 'cruel world'
 *
 * Now, insert the template into the DOM:
 *
 *       document.body.appendChild(greeting.element)
 *
 * This will result with the following inserted into the page:
 *
 * <body>
 *    <h1> <slot name="salutation">Goodbye</slot>, <slot name="recipient">cruel world</slot>!</h1>
 * </body>
 */
export default class SimpleTemplate {
  constructor(element) {
    /**
     * @property {Element} a clone of the template
     */
    this.element = element.content.firstElementChild.cloneNode(true)
    /**
     * @property {object} Dynamic object generated from <slot name> elements.
     */
    this.slot = {}

    // Create getters and setters for each slot
    for (let slot of this.element.querySelectorAll('slot[name]')) {
      createGettersAndSetters(this.slot, slot)
    }
  }

  /**
   * Create a new simple template given the id="" of an existing <template>
   * tag.
   *
   * @returns {SimpleTemplate} a brand new SimpleTemplate
   */
  static fromId(id) {
    let element = document.getElementById(id)
    if (element == null)
      throw new Error(`Could not find element with id="${id}"`)
    return new SimpleTemplate(element)
  }
}

function createGettersAndSetters(obj, slot) {
  return Object.defineProperty(obj, slot.name, {
    get: () => slot.innerText,
    set: (newValue) => slot.innerText = newValue,
    enumerable: true,
  })
}
