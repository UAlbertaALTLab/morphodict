/*
Name   : SearchSection
Inputs : Props ()
    
display: The resulting json image from the file. 
index  : the resulting index of the item from the returned array. 
       
Goal   : The purpose of this page is to display the search results gotten from user search. This is a single display of the word before a user picks the current file. 
       
*/

import { Tooltip, OverlayTrigger, Button } from "react-bootstrap";
import { Link, Redirect } from "react-router-dom";
import LikeWord from "./LikeWord";

const SearchSection = (props) => {
  //Information BTN tooltip(Here is where the info is to be typed out)
  const renderInformationToolTip = (props) => (
    <Tooltip id="button-tooltip" {...props}>
      {wordInformation["lemma_wordform"]["linguist_info"]["stem"]}
      <br />
      {information}
    </Tooltip>
  );

  const wordInformation = props.display;
  const wordsDefs = wordInformation["definitions"];

  let dictionary_index = function (type) {
    return type[0] === "CW" ? wolvengrey : misku;
  };

  const wolvengrey =
    "Wolvengrey, Arok, editor. Cree: Words. Regina, University of Regina Press, 2001";
  const misku =
    "Maskwacîs Dictionary. Maskwacîs, Maskwachees Cultural College, 1998.";

  let information = wordInformation["friendly_linguistic_breakdown_tail"];
  let inflectionCatagory =
    wordInformation["lemma_wordform"]["inflectional_category_linguistic"] +
    " (" +
    wordInformation["lemma_wordform"]["inflectional_category"] +
    ")"; // This is passed into LikeWord

  let infoBtn = "";
  let soundBtn = "";
  let sound = "a"; // Done as a test until api info is filled in sp2
  let wordBtn = "";

  if (information !== "") {
    infoBtn = (
      <Button
        variant="btn bg-white rounded shadow-none"
        onClick={() =>
          navigator.clipboard.writeText(
            wordInformation["lemma_wordform"]["linguist_info"]["stem"] +
              " - " +
              information
          )
        }
        size="lg"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          fill="currentColor"
          className="bi bi-info-circle"
          viewBox="0 0 16 16"
        >
          <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
          <path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z" />
        </svg>
      </Button>
    );
  }

  //Information on api only learned on 2/24/2022 moved into sp3
  if (sound !== "") {
    soundBtn = (
      <Button variant="btn bg-white rounded    " size="lg">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          fill="currentColor"
          className="bi bi-soundwave"
          viewBox="0 0 16 16"
        >
          <path
            fillRule="evenodd"
            d="M8.5 2a.5.5 0 0 1 .5.5v11a.5.5 0 0 1-1 0v-11a.5.5 0 0 1 .5-.5zm-2 2a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zm4 0a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zm-6 1.5A.5.5 0 0 1 5 6v4a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm8 0a.5.5 0 0 1 .5.5v4a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm-10 1A.5.5 0 0 1 3 7v2a.5.5 0 0 1-1 0V7a.5.5 0 0 1 .5-.5zm12 0a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0V7a.5.5 0 0 1 .5-.5z"
          />
        </svg>
      </Button>
    );
  }

  //change
  wordBtn = (
    <Button variant="btn bg-white rounded shadow-none">
      <Link
        to={{
          pathname: "/word/" + wordInformation.lemma_wordform.slug,
          state: {
          },
        }}
      >
        {wordInformation["lemma_wordform"]["text"][props.type] + ""}
      </Link>
      {/*When font-settings is built in sp3 make the check from the local store here */}
      <br />
    </Button>
  );

  let settings = JSON.parse(window.localStorage.getItem("settings"));
  let run = "";
  if(settings.both_sources){
    run = "CWMD"
  }
  if(settings.cw_source){
    run = "CW";
  }
  if(settings.md_source){
    run = "MD"
  }

  return (
    <div id="results" className="shadow p-3 mb-5 bg-body rounded">
      {wordInformation === "" &&
        <div>
          should never happen!
        </div>
      }
      <div className="d-flex flex-row">
        <div className="definition-title">{wordBtn}</div>

        <div className="definition__icon definition-title__tooltip-icon">
          <OverlayTrigger
            placement="bottom"
            delay={{ show: 250, hide: 400 }}
            overlay={renderInformationToolTip}
          >
            {infoBtn}
          </OverlayTrigger>
        </div>

        <div className="definition-title__play-icon">{soundBtn}</div>
      </div>
      <LikeWord
        likeWord={
          wordInformation["lemma_wordform"]["inflectional_category_linguistic"]
        }
        emoticon={wordInformation["lemma_wordform"]["wordclass_emoji"]}
        hoverInfo={inflectionCatagory}
      />

      <ul className="list-group text-center">
        {wordsDefs.filter(checkVal => run.includes(checkVal["source_ids"])).map((item, i) => (
          <li className="list-group-item " key={i}>
            {i + 1}. {item["text"]} :
            {
              <>
                <OverlayTrigger
                  key={1 + ""}
                  placement="bottom"
                  delay={{ show: 250, hide: 400 }}
                  overlay={
                    <Tooltip id="button-tooltip-dicts" {...props} key={i + ""}>
                      {dictionary_index(item["source_ids"])}
                    </Tooltip>
                  }
                >
                  {<span key={i}>{item["source_ids"]}</span>}
                </OverlayTrigger>
              </>
            }
            {/*TODO: make a better trigger for src so that they can copy the tooltip SP3*/}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default SearchSection;
