import { AiOutlineSound } from "react-icons/ai";
import { BsPlayFill } from "react-icons/bs";
import { Grid } from "@mui/material";
import { useState } from "react";
import Paradigm from "./Paradigm/Paradigm";
import { useQuery } from "react-query";

function WordEntry(props) {
  //const fakeData = fake_data;

  async function getWord() {
    let word = window.location.href.split("/")[4];
    if (word === "") {
      return null;
    }
    return fetch("http://10.2.10.152/local/word/" + word).then((res) =>
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
    wordform = data.nipaw_wordform.wordform;
    recordings = data.niya_recordings;
    paradigm = data.nipaw_wordform.paradigm;
    console.log(paradigm);
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
    setShowSpeakerMenu(true);
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
              <p className="multiple-recordings__help-text explainer">
                Choose a name from the dropdown to hear the word said by the
                speaker.
              </p>

              <select
                name="recordings-dropdown"
                data-cy="recordings-dropdown"
                className="multiple-recordings__dropdown"
              >
                <template id="template:speakerList">
                  <option>
                    <slot name="speakerName"></slot>,{" "}
                    <slot name="speakerDialect"></slot>
                  </option>
                </template>
              </select>

              <button
                className="multiple-recordings__action-button"
                data-action="play-current-recording"
                aria-label="Play recording"
                data-cy="play-selected-speaker"
              >
                <BsPlayFill></BsPlayFill>
              </button>
              <a
                className="multiple-recordings__action-button"
                data-action="learn-about-speaker"
                aria-label="Learn more about speaker"
                data-cy="learn-about-speaker"
                target="_blank"
                rel="noopener"
              >
                Learn more about the speaker.
              </a>
            </section>
          ) : null}

          <section className="definition__meanings" data-cy="meanings">
            <ol className="meanings">
              {wordform.definitions.map((def, index) => (
                <li className="meanings__meaning" key={index}>
                  {def.text}
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
