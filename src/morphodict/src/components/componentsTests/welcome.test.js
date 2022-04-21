import React from "react";
import { render, unmountComponentAtNode } from "react-dom";
import { act } from "react-dom/test-utils";

import About from "../Welcome";

let container = null;
beforeEach(() => {
  // setup a DOM element as a render target
  container = document.createElement("div");
  document.body.appendChild(container);
});

afterEach(() => {
  // cleanup on exiting
  unmountComponentAtNode(container);
  container.remove();
  container = null;
});

let value = "itwêwina is a Plains Cree Dictionary."

it("I as a user wish to see the following values inside the welcome page", () => {
  act(() => {    render(<About />, container);  });  expect(container.textContent).toContain(value);
});
