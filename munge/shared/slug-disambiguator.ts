import assert from "assert";
import { groupBy } from "lodash";

/**
 *
 * Return a unique list of short strings to disambiguate items.
 *
 * If there is only one input class, then no disambiguator is needed:
 *
 * > disambiguateSlugs(["NAI-1"])
 * ['']
 *
 * But if there are multiple input classes, e.g., for nêwokâtêw, then
 * return a unique disambiguator for each input:
 *
 * > disambiguateSlugs(["VAI-1", "NA-2", "VII-2v"])
 * ['@vai', '@n', '@vii']
 *
 * See the unit tests for more examples.
 * """
 *
 */
export function disambiguateSlugs(inputs: string[]) {
  inputs = inputs.map((i) => i.toLowerCase());
  assert(inputs.length >= 1);
  if (inputs.length === 1) {
    return [""];
  }
  const disambiguator = new SlugDisambiguator(inputs);
  disambiguator.disambiguate();
  return disambiguator.results().map((r) => `@${r.disambiguator}`);
}

/**
 * Non-exported class which handles actual disambiguation
 */
class SlugDisambiguator {
  private _items: InputItem[];
  private _uniqueKeys: Set<string>;

  constructor(inputs: string[]) {
    this._items = [];
    for (let i = 0; i < inputs.length; i++) {
      this._items.push(new InputItem(i, inputs[i]));
    }
    this._uniqueKeys = new Set();
  }

  unassignedItems() {
    return this._items.filter((x) => !x.assigned);
  }

  isDone() {
    return this.unassignedItems().length === 0;
  }

  private usingKeyGroups(keyFunc: (s: string) => string) {
    const groups = groupBy(this.unassignedItems(), (i) => keyFunc(i.value));
    for (const [key, items] of Object.entries(groups)) {
      if (items.length === 1) {
        this.assign(items[0], key);
      }
    }
  }

  private usingEnumeration() {
    for (const [ix, item] of this.unassignedItems().entries()) {
      this.assign(item, `${item.value}.${ix + 1}`);
    }
  }

  disambiguate() {
    function generalWordClass(inflectionalCategory: string) {
      return inflectionalCategory[0];
    }

    function specificWordClass(inflectionalCategory: string) {
      return inflectionalCategory.split("-")[0];
    }

    function inflectionalCategory(inflectionalCategory: string) {
      return inflectionalCategory;
    }

    for (const method of [
      () => this.usingKeyGroups(generalWordClass),
      () => this.usingKeyGroups(specificWordClass),
      () => this.usingKeyGroups(inflectionalCategory),
      () => this.usingEnumeration(),
    ]) {
      method();
      if (this.isDone()) {
        return;
      }
    }
    throw new Error(
      `Unable to disambiguate inputs ${JSON.stringify(
        this._items.map((i) => i.value)
      )}`
    );
  }

  assign(input: InputItem, key: string) {
    if (this._uniqueKeys.has(key)) {
      throw new Error(`attempt to re-use key ${key}`);
    }
    this._uniqueKeys.add(key);
    input.disambiguator = key;
  }

  results() {
    assert(this.isDone());
    return this._items;
  }
}

/**
 * Wrapper class to hold input items with disambiguator values. Among other
 * reasons to use a class instead of a plain array is that we may get duplicate
 * inputs which need to be tracked separately.
 */
class InputItem {
  index: number;
  value: string;
  disambiguator?: string;

  constructor(index: number, value: string) {
    this.index = index;
    this.value = value;
  }

  get assigned() {
    return !!this.disambiguator;
  }
}
