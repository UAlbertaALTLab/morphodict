import React from "react";
import { render, unmountComponentAtNode } from "react-dom";
import { act } from "react-dom/test-utils";

import Footer from "../Footer";

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

it("I as a user wish to see the following footer values", () => {
  act(() => {    render(<Footer />, container);  });  expect(container.textContent).toBe("HelpLegend of abbreviationsAboutContact usSettings View search results in: Community modeLinguist mode2019–2022 © Alberta Language Technology Lab. Modified icons copyright © 2019 Font Awesome, licensed under CC BY 4.0.");
  
});