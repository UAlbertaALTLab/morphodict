import React, { useState } from "react";
import MainPageCrk from "./crkeng/MainPage";
import MainPageSrs from "./srseng/MainPage";
import MainPageArp from "./arpeng/MainPage";
import MainPageCwd from "./cwdeng/MainPage";
import MainPageHdn from "./hdneng/MainPage";

let MainPage = import("./DefaultWelcomePage");

function updateOrthSettings(endonym, settings) {
    let title = process.env.REACT_APP_NAME;
    let welcome = process.env.REACT_APP_WELCOME;
    if (endonym === "nêhiyawêwin" || endonym === "nîhithawîwin") {
        if (settings.latn_x_macron) {
            title = process.env.REACT_APP_SRO_MACRONS_NAME;
            welcome = process.env.REACT_APP_SRO_MACRONS_WELCOME;
        } else if (settings.cmro) {
            title = process.env.REACT_APP_CMRO_NAME;
        } else if (settings.syllabics) {
            title = process.env.REACT_APP_SYLLABICS_NAME;
            welcome = process.env.REACT_APP_SYLLABICS_WELCOME;
        }
    }
    return [title, welcome];
}

function Welcome(props) {
    let title = process.env.REACT_APP_NAME;
    const description = process.env.REACT_APP_SUBTITLE;
    const endonym = process.env.REACT_APP_SOURCE_LANGUAGE_ENDONYM;
    let welcome = process.env.REACT_APP_WELCOME;
    const [settings, setSettings] = useState(JSON.parse(window.localStorage.getItem("settings")));

    window.addEventListener("settings", () => {
        setSettings(JSON.parse(window.localStorage.getItem("settings")));
    });

    [title, welcome] = updateOrthSettings(endonym, settings);

    return (
        <div>
            <article className="prose box">
                <h2 className="prose__heading no-italics">{welcome}</h2>

                <p>{title} is a {description}.</p>
                {endonym === "Tsuut'ina" ? <MainPageSrs/> :
                    endonym === "nêhiyawêwin" ? <MainPageCrk/> :
                        endonym === "Hinónoʼeitíít" ? <MainPageArp/> :
                            endonym === "nîhithawîwin" ? <MainPageCwd/> :
                                endonym === "X̲aad Kíl" ? <MainPageHdn/> :
                                    <MainPage/>}

            </article>
        </div>
    );
}

export default Welcome;
