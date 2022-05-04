import { AiOutlineSound } from "react-icons/ai";
import { BsPlayFill } from "react-icons/bs";
import { Grid } from "@mui/material";
import { useState } from "react";
import Paradigm from "./Paradigm/Paradigm";
import MultiPlayer from './MultiPlayer';
import { useQuery } from "react-query";

function WordEntry(props) {
  async function getWord() {
    let word = window.location.href.split("/")[4];
    if (word === "") {
      return null;
    }
    return fetch("http://127.0.0.1:8081/local/word/" + word).then((res) =>
      res.json()
    );
  }

  async function getWordRes() {
    let namedData = await getWord();
    try {
      namedData = JSON.parse(namedData);
      return namedData;
    } catch (err) {
      return null;
    }
  }

  const { isFetching, error, data, refetch } = useQuery(
    "getWordRes",
    () => getWordRes(),
    {
      refetchOnWindowFocus: false,
    }
  );
  let wordform = "";
  let recordings = "";
  let paradigm = "";
  let type = "Latn";

  if (!isFetching && !error && data !== null) {
    console.log(data);
    wordform = data.entry.wordform;
    recordings = data.entry.recordings;
    paradigm = data.entry.paradigm;
  }

  // MAYBE to do?
  let settings = JSON.parse(window.localStorage.getItem("settings"));
  if (settings.latn_x_macron) {
    type = "Latn-x-macron";
  }
  if (settings.syllabics) {
    type = "Cans";
  }

  window.addEventListener(type, (e) => {
    console.log(type);
  });

  const [showSpeakerMenu, setShowSpeakerMenu] = useState(false);
  const handleSoundPlay = () => {
    // TODO: NEED API
    // need sound api
    setShowSpeakerMenu(!showSpeakerMenu);
  };

  return (
    <>
      {!isFetching && !error && data !== null && (
        <article id="definition" className="definition">
          <header className="definition__header">
            <Grid container direction="row">
              <Grid item>
                <h1 id="head" className="definition-title">
                  <dfn className="definition__matched-head">
                    <data id="data:head" value="{{ lemma.text }}">
                      {wordform["text"][type]}
                    </data>
                  </dfn>
                </h1>
              </Grid>
              <Grid item>
                <button
                  className="definition__icon"
                  onClick={() => handleSoundPlay()}
                  style={{
                    marginTop: "20%",
                    marginLeft: "0.5em",
                  }}
                >
                  <AiOutlineSound className="definition-title__play-button"></AiOutlineSound>
                </button>
              </Grid>
            </Grid>
            {/* include "CreeDictionary/components/definition__elaboration.html" with lemma=wordform verbose=True */}
          </header>

          {showSpeakerMenu ? (
            <section
              className="multiple-recordings"
              id="recordings-dropdown"
              data-cy="multiple-recordings"
            >
              <MultiPlayer recordings={recordings} />
            </section>
          ) : null}

          <section className="definition__meanings" data-cy="meanings">
            <ol className="meanings">
              {wordform.definitions.map((def, index) => (
                <li className="meanings__meaning" key={index}>
                  {def.text} {def.source_id}
                </li>
              ))}
            </ol>
          </section>

          <section>
            <Paradigm paradigm={paradigm}></Paradigm>
          </section>

        </article>
      )}
    </>
  );
}
export default WordEntry;
