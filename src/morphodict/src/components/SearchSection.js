/*
Name   : SearchSection
Inputs : Props ()
    
display: The resulting json image from the file. 
index  : the resulting index of the item from the returned array. 
       
Goal   : The purpose of this page is to display the search results gotten from user search. This is a single display of the word before a user picks the current file. 
       
*/

import React, {useState} from "react";
import {Tooltip, OverlayTrigger, Button} from "react-bootstrap";
import {Link, Redirect} from "react-router-dom";
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import {faVolumeUp, faInfoCircle} from '@fortawesome/free-solid-svg-icons'
import LikeWord from "./LikeWord";

function getInflectionalCategory(wordInformation) {
    try {
        return wordInformation["lemma_wordform"]["inflectional_category_linguistic"] +
            " (" +
            wordInformation["lemma_wordform"]["inflectional_category"] +
            ")";
    } catch (TypeError) {
        return wordInformation["inflectional_category_linguistic"] +
            " (" +
            wordInformation["inflectional_category"] +
            ")";
    }
}

function getInflectionalCategoryPlainEnglish(wordInformation) {
    try {
        return wordInformation["lemma_wordform"]["inflectional_category_linguistic"] +
            " (" +
            wordInformation["lemma_wordform"]["inflectional_category_plain_english"] +
            ")";
    } catch (TypeError) {
        return wordInformation["inflectional_category_linguistic"] +
            " (" +
            wordInformation["inflectional_category_plain_english"] +
            ")";
    }
}

const SearchSection = (props) => {

    const getInformation = () => {
        console.log("HERE:", wordInformation);
        if (wordInformation["relabelled_fst_analysis"]) {
            switch (settings.label) {
                case "ENGLISH":
                    return wordInformation["relabelled_fst_analysis"]["plain_english"];
                case "LINGUISTIC (LONG)":
                    return wordInformation["relabelled_fst_analysis"]["linguistic_long"];
                case "LINGUISTIC (SHORT)":
                    return wordInformation["relabelled_fst_analysis"]["linguistic_short"];
                case "NÊHIYAWÊWIN":
                    return wordInformation["relabelled_fst_analysis"]["source_language"];
                default:
                    return wordInformation["relabelled_fst_analysis"]
            }
        } else if (wordInformation["friendly_linguistic_breakdown_tail"]) {
            return wordInformation["friendly_linguistic_breakdown_tail"];
        } else {
            return [];
        }
    }
    //Information BTN tooltip(Here is where the info is to be typed out)
    let [settings, setSettings] = useState(JSON.parse(window.localStorage.getItem("settings")));
    window.addEventListener("settings", () => {
        setSettings(JSON.parse(window.localStorage.getItem("settings")));
    });
    const getStem = () => {
        if (wordInformation["lemma_wordform"]) {
            if (wordInformation["lemma_wordform"]["linguist_info"]) {
                if (wordInformation["lemma_wordform"]["linguist_info"]["stem"]) {
                    return wordInformation["lemma_wordform"]["linguist_info"]["stem"];
                }
            }
        } else if (wordInformation["linguist_info"]) {
            if (wordInformation["linguist_info"]["stem"]) {
                return wordInformation["linguist_info"]["stem"];
            }
        }
        return wordInformation["wordform_text"][displayType]
    }

    let wordInformation = props.display;
    if (!wordInformation) {
        return (<div>Something went wrong here</div>);
    }

    let information = getInformation(wordInformation, settings);

    const renderInformationToolTip = (props) => (
        <Tooltip data-cy="infoButtonInfo" id="button-tooltip" {...props}>
            {getStem()}
            <br/>
            {information.map((item, i) => (<li>{item}</li>))}
        </Tooltip>
    );

    const wordsDefs = wordInformation["definitions"];
    const displayType = props.type;

    const displayWord = function () {
        //TODO: this try catch is broken

        const settings = JSON.parse(window.localStorage.getItem("settings"));
        try {
            if (settings.morphemes_everywhere || settings.morphemes_headers) {
                return wordInformation["morphemes"][displayType].join('/');
            } else {
                return wordInformation['wordform_text'][displayType];
            }
        } catch (TypeError) {
            try {
                return wordInformation['wordform_text'][displayType];
            } catch (TypeError) {
                return wordInformation['text'];
            }
        }
        return wordInformation;
    }

    let dictionary_index = function (type) {
        try {
            return citationChoices[type[0]]
        } catch (KeyError) {
            return maskwacis
        }
    };

    const wolvengrey =
        "Wolvengrey, Arok, editor. Cree: Words. Regina, University of Regina Press, 2001";
    const maskwacis =
        "Maskwacîs Dictionary. Maskwacîs, Maskwachees Cultural College, 1998.";
    const aecd = "Alberta Elders' Cree Dictionary/alberta ohci kehtehayak nehiyaw otwestamâkewasinahikan, compiled by Nancy LeClaire and George Cardinal, edited by Earle H. Waugh. Edmonton: University of Alberta Press, 2002."
    const tvpd = "Starlight, Bruce, Gary Donovan, and Christopher Cox, editors. Tsuut'ina Verb Phrase Dictionary"

    const citationChoices = {"CW": wolvengrey, "MD": maskwacis, "AECD": aecd, "TVPD": tvpd}

    const inflectionalCategory = getInflectionalCategory(wordInformation); // This is passed into LikeWord
    const inflectionalCategoryPlainEnglish = getInflectionalCategoryPlainEnglish(wordInformation); // This is passed into LikeWord

    const getLemmaWordform = () => {
        try {
            return wordInformation["lemma_wordform"];
        } catch (TypeError) {
            return "";
        }
    }

    let infoBtn = "";
    let soundBtn = "";
    let sound = wordInformation["recording"];
    let wordBtn = "";
    let lemmaWordform = getLemmaWordform();

    const handleSoundPlay = () => {
        const audio = new Audio(sound);
        audio.play();
    };

    if (information !== "") {
        infoBtn = (
            <Button
                variant="btn bg-white rounded shadow-none"
                onClick={() =>
                    navigator.clipboard.writeText(
                        getStem() +
                        " - " +
                        information
                    )
                }
                data-cy="infoButton">
                <FontAwesomeIcon icon={faInfoCircle} size="sm"/>
            </Button>
        );
    }

    //Information on api only learned on 2/24/2022 moved into sp3
    if (sound !== "") {
        soundBtn = (
            <Button variant="btn bg-white rounded"
                    onClick={handleSoundPlay}
                    data-cy="playRecording">
                <FontAwesomeIcon icon={faVolumeUp} size="sm"/>
            </Button>
        );
    }

    const getEmoticon = () => {
        try {
            return wordInformation["lemma_wordform"]["wordclass_emoji"];
        } catch (TypeError) {
            try {
                return props.emoticon;
            } catch (e) {
                return "";
            }
        }
    }

    const getSlug = () => {
        try {
            return wordInformation["lemma_wordform"]["slug"];
        } catch (TypeError) {
            try {
                return props.slug;
            } catch (e) {
                return "";
            }
        }
    }

    const getIc = () => {
        if (wordInformation["lemma_wordform"]) {
            return wordInformation["lemma_wordform"];
        } else {
            return wordInformation;
        }
    }

    const shouldNotDisplayFormOf = () => {
        if (lemmaWordform) {
            return lemmaWordform["wordform_text"][displayType] === wordInformation["wordform_text"][displayType];
        } else {
            return true;
        }
    }

    const emoticon = getEmoticon();
    const slug = getSlug();
    const ic = getIc();

    //change
    wordBtn = (
        <Button variant="btn bg-white rounded shadow-none">
            <Link
                to={{
                    pathname: "/word/" + slug,
                    state: {},
                }}
                data-cy="lemmaLink"
            >
                {displayWord()}
            </Link>
            {/*When font-settings is built in sp3 make the check from the local store here */}
            <br/>
        </Button>
    );

    return (
        <div id="results" className="shadow p-3 mb-5 bg-body rounded" data-cy="searchResults">
            {wordInformation === "" &&
            <div>
                should never happen!
            </div>
            }
            <div className="d-flex flex-row">
                <div className="definition-title" data-cy="definitionTitle">{wordBtn}</div>

                <div className="definition__icon definition-title__tooltip-icon">
                    <OverlayTrigger
                        placement="bottom"
                        delay={{show: 250, hide: 400}}
                        overlay={renderInformationToolTip}
                    >
                        {infoBtn}
                    </OverlayTrigger>
                </div>

                <div className="definition-title__play-icon">{soundBtn}</div>
            </div>

            <LikeWord
                wordform={wordInformation}
            />
            <ul className="list-group text-center">
                {wordsDefs.map((item, i) => (
                    <li className="list-group-item " data-cy="definitionText" key={i}>
                        {i + 1}. {item["text"]} &nbsp; {item.source_ids.map((i, index) => (
                        <OverlayTrigger
                            placement="bottom"
                            delay={{show: 250, hide: 400}}
                            overlay={<Tooltip id="button-tooltip-dicts" {...props} key={index + ""}>
                                {citationChoices[i]}
                            </Tooltip>}
                        >
                            <span data-cy="citation">{i}&nbsp;</span>
                        </OverlayTrigger>))}
                        {/*TODO: make a better trigger for src so that they can copy the tooltip SP3*/}
                    </li>
                ))}
            </ul>
            {shouldNotDisplayFormOf() ? <></> :
                <><p><i>Form of:</i></p>
                    <SearchSection
                        key={props.index + 0.5}
                        display={lemmaWordform}
                        index={props.index + 0.5}
                        type={props.type}
                        emoji={getEmoticon()}
                        slug={getSlug()}
                        information={getInformation()}
                    /></>}

        </div>
    );
};

export default SearchSection;
