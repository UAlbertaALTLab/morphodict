/*
Name   : LikeWord
Inputs : Props ()
       
    likeWord        : a similer word to the current word found.   
    emoticon        : the emoticon that will show the current word 
    wordInformation : class of the word(current) information
       
Goal         : Show word information and also provide the ability to highlight and copy that information to the users clipboard. 
*/

import React, {useState} from "react";
import {Tooltip, OverlayTrigger, Button} from "react-bootstrap";

function updateLabelSettings(label, icPlainEnglish, icLinguisticLong, icLinguisticShort, icSourceLanguage) {
    let primaryInfo = "";
    let secondaryInfo = "";
    if (!icLinguisticLong) {
        icLinguisticLong = icLinguisticShort;
    }
    switch (label) {
        case "ENGLISH":
            primaryInfo = icPlainEnglish;
            secondaryInfo = icLinguisticShort + " - " + icSourceLanguage;
            return [primaryInfo, secondaryInfo];
        case "LINGUISTIC (LONG)":
            primaryInfo = icLinguisticLong;
            secondaryInfo = icLinguisticShort + " - " + icPlainEnglish + " - " + icSourceLanguage;
            return [primaryInfo, secondaryInfo];
        case "LINGUISTIC (SHORT)":
            primaryInfo = icLinguisticLong;
            secondaryInfo = icPlainEnglish + " - " + icSourceLanguage;
            return [primaryInfo, secondaryInfo];
        case "NÊHIYAWÊWIN":
            primaryInfo = icSourceLanguage;
            secondaryInfo = icLinguisticShort + " - " + icPlainEnglish;
            return [primaryInfo, secondaryInfo];
        default:
            return [primaryInfo, secondaryInfo];
    }
}

function getDisplayIc(wordform) {
    if (wordform["lemma_wordform"]) {
        return wordform.lemma_wordform.inflectional_category;
    } else {
        return wordform.inflectional_category;
    }

}

function getRelabelledIc(wordform) {
    if (wordform["lemma_wordform"]) {
        return wordform.lemma_wordform.inflectional_category_relabelled
    } else {
        return wordform;
    }
}

function getEmoticon(wordform) {
    if (wordform["lemma_wordform"]) {
        return wordform.lemma_wordform.wordclass_emoji;
    } else {
        return wordform.wordclass_emoji;
    }
}

const LikeWord = (props) => {
    const wordform = props.wordform;
    const relabelledIc = getRelabelledIc(wordform);
    let icLinguisticShort = wordform.inflectional_category_linguistic;
    let icLinguisticLong = wordform.inflectional_category_linguistic;;
    let icSourceLanguage = "";
    let icPlainEnglish = wordform.inflectional_category_plain_english;
    if (relabelledIc !== wordform) {
        icLinguisticShort = relabelledIc.linguistic_short;
        icLinguisticLong = relabelledIc.linguistic_long;
        icSourceLanguage = relabelledIc.source_language;
        icPlainEnglish = relabelledIc.plain_english
        if (icPlainEnglish === "Action word") {
            icPlainEnglish += " - " + wordform.lemma_wordform.inflectional_category_plain_english;
        }
    }
    const displayIc = getDisplayIc(wordform);
    console.log(displayIc);
    let emoticon = getEmoticon(wordform);
    let [settings, setSettings] = useState(JSON.parse(window.localStorage.getItem("settings")));

    if (emoticon && emoticon.includes("🧑🏽")) {
        emoticon = emoticon.replaceAll("🧑🏽", settings.active_emoji);
    }

    const showIc = settings.showIC;

    const showEmoji = settings.showEmoji;
    if (showEmoji === false) {
        emoticon = "";
    } else {
        emoticon = emoticon + " - "
    }

    let primaryInfo = "";
    let secondaryInfo = "";

    window.addEventListener("settings", () => {
        setSettings(JSON.parse(window.localStorage.getItem("settings")));
    });

    [primaryInfo, secondaryInfo] = updateLabelSettings(settings.label, icPlainEnglish, icLinguisticLong, icLinguisticShort, icSourceLanguage);


    const infoLink = (
        <Button
            variant="btn bg-white rounded shadow-none text-decoration-underline"
            onClick={() => navigator.clipboard.writeText(secondaryInfo)}
        >
            {primaryInfo}
        </Button>
    );

    const renderInformationToolTip = (props) => (
        <Tooltip id="word-info-tooltip" {...props}>
            {secondaryInfo}
        </Tooltip>
    );

    return (<>
            <div data-cy="elaboration" className="container">
                <div className="d-flex flex-row">
                    <div className="mb-auto p-2">
                        <span data-cy="inflectionalCategory">{(showIc) ? displayIc + " " : ""}</span>
                        <span data-cy="wordclassEmoji">{showEmoji ? emoticon + " " : ""}</span>
                        <OverlayTrigger
                            placement="bottom"
                            delay={{show: 250, hide: 400}}
                            overlay={renderInformationToolTip}
                        >
                            {infoLink}
                        </OverlayTrigger>
                    </div>
                </div>
            </div>
        </>
    );
};

export default LikeWord;
