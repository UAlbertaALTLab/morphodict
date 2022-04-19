/*
Name   : LikeWord
Inputs : Props ()
       
    likeWord        : a similer word to the current word found.   
    emoticon        : the emoticon that will show the current word 
    wordInformation : class of the word(current) information
       
Goal         : Show word information and also provide the ability to highlight and copy that information to the users clipboard. 
*/

import { Tooltip, OverlayTrigger, Button } from "react-bootstrap";

const LikeWord = (props) => {
  const likeWord = props.likeWord;
  let emoticon = props.emoticon;
  const wordInformation = props.hoverInfo;

  let settings = JSON.parse(window.localStorage.getItem("settings"));
  if (emoticon && emoticon.includes("🧑🏽")) {
    emoticon = emoticon.replaceAll("🧑🏽", settings.active_emoti);
  }

  //Don't exactly understand the whole emoticon thing.
  //Will need to ask cline to explain that information
  //to me. :(
  const infoLink = (
    <Button
      variant="btn bg-white rounded shadow-none text-decoration-underline"
      onClick={() => navigator.clipboard.writeText(wordInformation)}
    >
      {emoticon} — {likeWord}
    </Button>
  );

  const renderInformationToolTip = (props) => (
    <Tooltip id="word-info-tooltip" {...props}>
      {wordInformation}
    </Tooltip>
  );

  return (
    <>
      {likeWord !== null && (
        <>
          <div className="container">
            <div className="d-flex flex-row">
              <div className="mb-auto p-2">
                <OverlayTrigger
                  placement="bottom"
                  delay={{ show: 250, hide: 400 }}
                  overlay={renderInformationToolTip}
                >
                  {infoLink}
                </OverlayTrigger>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
};

export default LikeWord;
