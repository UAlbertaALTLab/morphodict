import { describe } from "mocha";
import { expect } from "chai";
import { stringDistance } from "./util";

describe("editDistance", function () {
  for (const [a, b, dist] of [
    ["a", "a", 0],
    ["ax", "a", 1],
    ["â", "a", 0.5],
    ["foo", "bar", 3],
    ["foo", "fojjjo", 3],
    // test twiddle
    ["hello world", "hello wordl", 1],
    ["Hello", "hello", 0.5],
  ] as [string, string, number][]) {
    it(`returns edit distance ${dist} for ${JSON.stringify(
      a
    )} vs ${JSON.stringify(b)}`, function () {
      expect(stringDistance(a, b)).to.equal(dist);
    });
  }
});
