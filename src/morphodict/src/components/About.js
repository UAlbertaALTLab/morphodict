import "./style.css";

function About(props) {
  return (
    <div>
      <section id="source-materials" className="prose box box--spaced">
        <h2 className="prose__section-title">Source Materials</h2>

        <h3 className="prose__heading"> Plains Cree / nêhiyawêwin</h3>
        <p>
          The computational model for analyzing Plains Cree / nêhiyawêwin' words
          and generating the various inflectional paradigms is based on the
          lexical materials and scientific research in{" "}
          <a
            href="https://uofrpress.ca/Books/C/Cree-Words"
            className="source-title"
          >
            nêhiyawêwin : itwêwina / Cree: Words
          </a>{" "}
          (Compiled by Arok Wolvengrey. Regina: Canadian Plains Research Center,
          2001), and described in{" "}
          <a
            href="http://altlab.artsrn.ualberta.ca/wp-content/uploads/2019/01/Snoek_et_al_CEL1_2014.pdf"
            className="source-title"
          >
            Modeling the Noun Morphology of Plains Cree
          </a>{" "}
          (Conor Snoek, Dorothy Thunder, Kaidi Lõo, Antti Arppe, Jordan Lachler,
          Sjur Moshagen &amp; Trond Trosterud, 2014) and{" "}
          <a
            href="http://altlab.artsrn.ualberta.ca/wp-content/uploads/2019/01/Harrigan_Schmirler_Arppe_Antonsen_Trosterud_Wolvengrey_2017fc.pdf"
            className="source-title"
          >
            Learning from the Computational Modeling of Plains Cree Verbs
          </a>{" "}
          (Atticus G. Harrigan, Katherine Schmirler, Antti Arppe, Lene Antonsen,
          Trond Trosterud &amp; Arok Wolvengrey. Morphology, 2018).
        </p>

        <h3 className="prose__heading">
          {" "}
          Plains Cree / nêhiyawêwin ↔ English / âkayâsîmowin{" "}
        </h3>
        <p>
          The bilingual Dictionary for Plains Cree / nêhiyawêwin and English /
          âkayâsîmowin is based on the lexical materials in{" "}
          <a
            href="https://uofrpress.ca/Books/C/Cree-Words"
            className="source-title"
          >
            nêhiyawêwin : itwêwina / Cree: Words
          </a>
          . (Compiled by Arok Wolvengrey. Regina: Canadian Plains Research
          Center, 2001), and in the{" "}
          <a
            href="https://www.altlab.dev/maskwacis/dictionary.html"
            className="source-title"
          >
            Maskwacîs Dictionary of Cree Words / Nêhiyaw Pîkiskwêwinisa
          </a>{" "}
          (Maskwachees Cultural College, Maskwacîs, 2009).
        </p>

        <h3 className="prose__heading"> Spoken Cree — nêhiyaw-pîkiskwêwina</h3>
        <p>
          The careful pronunciations of the Cree words by first-language
          speakers in Maskwacîs, Alberta, have been recorded in the joint
          project{" "}
          <a href="https://www.altlab.dev/maskwacis/" className="source-title">
            Spoken Dictionary of Maskwacîs Cree – nêhiyaw-pîkiskwêwina
            maskwacîsihk
          </a>{" "}
          between then Miyo Wahkohtowin Education, now{" "}
          <a href="https://www.maskwacised.ca/">
            Maskwacîs Education Schools Commission
          </a>{" "}
          and the{" "}
          <a href="http://altlab.artsrn.ualberta.ca/">
            Alberta Language Technology Lab
          </a>{" "}
          (2014–on-going). The pronunciations of the Cree words have been
          graciously provided by the individuals at{" "}
          <a href="https://www.altlab.dev/maskwacis/Speakers/speakers.html">
            this page
          </a>
          .
        </p>
      </section>

      <section id="credits" className="prose box box--spaced">
        <h2 className="prose__section-title">Credits</h2>

        <p>
          itwêwina is{" "}
          <a href="https://github.com/UAlbertaALTLab/morphodict">
            an open-source project
          </a>
          . You can view{" "}
          <a href="https://github.com/UAlbertaALTLab/morphodict/blob/main/AUTHORS.md">
            the list of the contributors here.
          </a>
        </p>

        <p> The mîkiwâhp (teepee) logo was created by Tasha Powers. </p>

        <p>
          This project has been supported by the Social Sciences and Humanities
          Research Council (SSHRC) of Canada, through grants 895-2019-1012,
          611-2016-0207, and 890-2013-0047, and it contains contributions from
          the{" "}
          <a href="https://nrc.canada.ca/en/research-development/research-collaboration/programs/canadian-indigenous-languages-technology-project">
            Canadian Indigenous languages technology project
          </a>
          , a part of the{" "}
          <a href="https://nrc.canada.ca/en">
            National Research Council Canada
          </a>
          .
        </p>

        <div className="partner-logos">
          <a
            className="partner-logos__logo partner-logos__logo--full-width"
            href="https://www.sshrc-crsh.gc.ca/home-accueil-eng.aspx"
          >
            <img
              className="sshrc-crsh-logo"
              alt="Social Sciences and Humanities Research Council"
            ></img>
          </a>
          <a className="partner-logos__logo" href="https://www.maskwacised.ca/">
            <img className="mesc-logo" alt="MESC"></img>
          </a>
          <a className="partner-logos__logo" href="http://fnuniv.ca/">
            <img className="fnu-logo" alt="First Nations University"></img>
          </a>
          <a
            className="partner-logos__logo"
            href="https://altlab.artsrn.ualberta.ca/"
          >
            <img className="uofa-logo" alt="University of Alberta"></img>
          </a>
          <a
            className="partner-logos__logo partner-logos__logo--full-width"
            href="https://nrc.canada.ca/en/research-development/research-collaboration/programs/canadian-indigenous-languages-technology-project"
          >
            <img
              className="nrc-cnrc-logo"
              alt="National Research Council Canada"
            ></img>
          </a>
        </div>
      </section>

      <section id="contact-us" className="prose box box--spaced">
        <h2 className="prose__section-title">Contact us</h2>
        <p>
          Find a problem? Email us at{" "}
          <a href="mailto:altlab@ualberta.ca" className="about__link">
            altlab@ualberta.ca
          </a>
          .
        </p>
      </section>
    </div>
  );
}

export default About;
