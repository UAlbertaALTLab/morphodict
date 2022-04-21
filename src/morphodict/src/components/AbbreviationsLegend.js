import "./style.css";
function AbbreviationsLegend(props) {
  return (
    <section id="legend" className="prose box box--spaced legend">
      <h2 className="proce__section-title">
        Legend of abbreviations and terms
      </h2>

      <dl>
        <dt>s/he, she, he</dt>
        <dd>
          <strong>s</strong>he, <strong>h</strong>e, or (singular) th
          <strong>e</strong>y. Used in definitions to stand for the
          <strong>animate actor</strong>, which is mostly human but can
          sometimes refer to other animate entities as well. The approximate
          equivalent to the Cree pronoun <a href="/word/wiya">wiya</a>. (e.g.{" "}
          <q>
            <dfn>s/he</dfn> sees;
            <dfn>s/he</dfn> sees something; <dfn>s/he</dfn> sees someone
          </q>
          )
        </dd>

        <dt>s.t., it</dt>
        <dd>
          <strong>s</strong>ome<strong>t</strong>hing. Used in definitions to
          stand for the <strong>inanimate goal</strong>. (e.g.{" "}
          <q>
            s/he sees
            <dfn>s.t.</dfn>, i.e. something; s/he sees <dfn>it</dfn>
          </q>
          )
        </dd>

        <dt>s.o., her, him</dt>
        <dd>
          <strong>s</strong>ome<strong>o</strong>ne, but can also mean
          “something animate” like <a href="/word/pahkwêsikan">pahkwêsikan</a>{" "}
          or <a href="/word/asikan">asikan</a>. Used in definitions to stand for
          the
          <strong>animate goal</strong>. (e.g.{" "}
          <q>
            s/he sees <dfn>s.o.</dfn>, i.e. someone; s/he sees <dfn>him</dfn>;
            s/he sees <dfn>her</dfn>
          </q>
          )
        </dd>

        <dt>it</dt>
        <dd>
          Used in definitions to stand for the <strong>inanimate actor</strong>{" "}
          (e.g.{" "}
          <q>
            <dfn>it</dfn> is blue
          </q>
          ) or
          <strong>existential subject</strong> for impersonal verbs (the “it” in{" "}
          <q>
            <dfn>it</dfn> is raining
          </q>
          ).
        </dd>
      </dl>
    </section>
  );
}
export default AbbreviationsLegend;
