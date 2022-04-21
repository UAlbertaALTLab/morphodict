import React from "react";
import { render, unmountComponentAtNode } from "react-dom";
import { act } from "react-dom/test-utils";

import About from "../About";

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

let conactValue = "Source Materials Plains Cree / nêhiyawêwinThe computational model for analyzing Plains Cree / nêhiyawêwin' words and generating the various inflectional paradigms is based on the lexical materials and scientific research in nêhiyawêwin : itwêwina / Cree: Words (Compiled by Arok Wolvengrey. Regina: Canadian Plains Research Center, 2001), and described in Modeling the Noun Morphology of Plains Cree (Conor Snoek, Dorothy Thunder, Kaidi Lõo, Antti Arppe, Jordan Lachler, Sjur Moshagen & Trond Trosterud, 2014) and Learning from the Computational Modeling of Plains Cree Verbs (Atticus G. Harrigan, Katherine Schmirler, Antti Arppe, Lene Antonsen, Trond Trosterud & Arok Wolvengrey. Morphology, 2018). Plains Cree / nêhiyawêwin ↔ English / âkayâsîmowin The bilingual Dictionary for Plains Cree / nêhiyawêwin and English / âkayâsîmowin is based on the lexical materials in nêhiyawêwin : itwêwina / Cree: Words. (Compiled by Arok Wolvengrey. Regina: Canadian Plains Research Center, 2001), and in the Maskwacîs Dictionary of Cree Words / Nêhiyaw Pîkiskwêwinisa (Maskwachees Cultural College, Maskwacîs, 2009). Spoken Cree — nêhiyaw-pîkiskwêwinaThe careful pronunciations of the Cree words by first-language speakers in Maskwacîs, Alberta, have been recorded in the joint project Spoken Dictionary of Maskwacîs Cree – nêhiyaw-pîkiskwêwina maskwacîsihk between then Miyo Wahkohtowin Education, now Maskwacîs Education Schools Commission and the Alberta Language Technology Lab (2014–on-going). The pronunciations of the Cree words have been graciously provided by the individuals at this page.Creditsitwêwina is an open-source project. You can view the list of the contributors here. The mîkiwâhp (teepee) logo was created by Tasha Powers. This project has been supported by the Social Sciences and Humanities Research Council (SSHRC) of Canada, through grants 895-2019-1012, 611-2016-0207, and 890-2013-0047, and it contains contributions from the Canadian Indigenous languages technology project, a part of the National Research Council Canada.Contact usFind a problem? Email us at altlab@ualberta.ca."

it("I as a user wish to see the following values inside contact us", () => {
  act(() => {    render(<About />, container);  });  expect(container.textContent).toBe(conactValue);
});