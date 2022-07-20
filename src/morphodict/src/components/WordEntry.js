import { AiOutlineSound } from "react-icons/ai";
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
    return fetch("http://127.0.0.1:8000/api/word/" + word).then((res) =>
      res.json()
    );
  }

  async function getWordRes() {
    let namedData = await getWord();
    console.log(namedData);
    try {
      // namedData = JSON.parse(namedData);
      return namedData;
    } catch (err) {
      console.log(err);
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
  console.log(isFetching, error, data);
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

  let recs = [];
  if (recordings) {
    recs = recordings.map((recording) =>
      <option onClick={submittedAudio} key={recording.url} data-link={recording.speaker_bio_url} value={recording.recording_url}>
          {recording.speaker_name}, {recording.language[0]}
      </option>
    );
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

  const handleSoundPlay = () => {
    const recToPlay = recordings[0].recording_url;
    const audio = new Audio(recToPlay);
    audio.play();
  };

  function submittedAudio(){
    const link = document.getElementById("audio_select").value;
    const audio = new Audio(link);
    audio.play();
  }

  const audioChanged = (e) => {
    const idx = e.target.selectedIndex;
    const option = e.target.querySelectorAll('option')[idx];
    const link = option.getAttribute('data-link');
    const linkElement = document.getElementById("learnMoreLink");
    linkElement.href = link;
    submittedAudio();
    return false;
  }

  return (
    <>
      {/*<p>{data}</p>*/}
      {(!isFetching && !error && data !== null) ? (
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
          </header>

          {recordings[0] ? (<section
              className="multiple-recordings"
              id="recordings-dropdown"
              data-cy="multiple-recordings"
              key={"speakerDropdownSection"}
            >
              <h6 key={"speakerDropdownHelpText"}>Choose a name from the dropdown to hear the word said by the speaker.</h6>
              <select id="audio_select" onChange={audioChanged}>
              {recs}
            </select>
            <button onClick={submittedAudio}>&#9655;</button> <a href={recordings[0].speaker_bio_url} id={"learnMoreLink"} target={"_blank"}>Learn more about the speaker...</a>
            </section> ) : <></> }

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
      ) : <></> }
    </>
  );
}

export default WordEntry;
