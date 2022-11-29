import "./style.css";
import morphodict_default_logo from "../static/morphodict-default-logo-192.png";

import React, {useState} from "react";
import {TextField} from "@mui/material";
import {Redirect} from "react-router-dom";
import Settings from "../HelperClasses/SettingClass";

const crkSettings = {
    Latn: "SRO (êîôâ)",
    "Latn-x-macron": "SRO (ēīōā)",
    Cans: "Syllabics",
    ENGLISH: "English Labels",
    "LINGUISTIC (LONG)": "Linguistic Labels (long)",
    "LINGUISTIC (SHORT)": "Linguistic Labels (short)",
    NÊHIYAWÊWIN: "nêhiyawêwin labels",
}

const srsSettings = {
    ENGLISH: "English Labels",
    "LINGUISTIC (LONG)": "Linguistic Labels (long)",
    "LINGUISTIC (SHORT)": "Linguistic Labels (short)",
    "TSUUT'INA": "Tsuut'ina labels",
}

const hdnSettings = {
    ENGLISH: "English Labels",
    "LINGUISTIC (LONG)": "Linguistic Labels (long)",
    "LINGUISTIC (SHORT)": "Linguistic Labels (short)",
    "X̲AAD KÍL": "X̲aad Kíl labels",
}

const arpSettings = {
    ENGLISH: "English Labels",
    "LINGUISTIC (LONG)": "Linguistic Labels (long)",
    "LINGUISTIC (SHORT)": "Linguistic Labels (short)",
    "HINÓNO'ÉÍ": "Hinónoʼeitíít labels",
}

const cwdSettings = {
    "Latn-x-macron": "SRO (ēīōā)",
    CMRO: "CMRO",
    Cans: "Syllabics",
    ENGLISH: "English Labels",
    "LINGUISTIC (LONG)": "Linguistic Labels (long)",
    "LINGUISTIC (SHORT)": "Linguistic Labels (short)",
    NÊHIYAWÊWIN: "nîhithawîwin labels",
}

let defaultSettings;
switch (process.env.REACT_APP_ISO_CODE) {
    case "srs":
        defaultSettings = srsSettings;
        break;
    case "crk":
        defaultSettings = crkSettings;
        break;
    case "hdn":
        defaultSettings = hdnSettings;
        break;
    case "arp":
        defaultSettings = arpSettings;
        break;
    case "cwd":
        defaultSettings = cwdSettings;
        break;
    default:
        defaultSettings = crkSettings;
}

function Header(props) {
    const [dictionaryName, setDictionaryName] = useState(process.env.REACT_APP_NAME);
    const description = process.env.REACT_APP_SUBTITLE;
    const sourceLanguageName = process.env.REACT_APP_SOURCE_LANGUAGE_ENDONYM;
    const [queryString, setQueryString] = useState("");
    const [query, setQuery] = useState(false);
    const [type, setDispType] = useState("Latn");
    const settingMenu = defaultSettings;

    if (!window.localStorage.getItem("settings")) {
        window.localStorage.setItem("settings", JSON.stringify(new Settings()));
    }

    const updateDictionaryName = () => {
        let settings = JSON.parse(window.localStorage.getItem("settings"));

        if (sourceLanguageName === "nêhiyawêwin") {
            if (settings.latn) {
                setDictionaryName(process.env.REACT_APP_NAME);
            } else if (settings.latn_x_macron) {
                setDictionaryName(process.env.REACT_APP_SRO_MACRONS_NAME);
            } else if (settings.syllabics) {
                setDictionaryName(process.env.REACT_APP_SYLLABICS_NAME);
            }
        }
    }

    const handleSettingChange = (value) => {
        let settings = JSON.parse(window.localStorage.getItem("settings"));

        switch (value) {
            case "Latn":
                settings.latn = true;
                settings.latn_x_macron = false;
                settings.syllabics = false;
                settings.cmro = false;
                if (sourceLanguageName === "nêhiyawêwin") {
                    setDictionaryName(process.env.REACT_APP_NAME);
                }
                setDispType("Latn");
                break;
            case "Latn-x-macron":
                settings.latn = false;
                settings.latn_x_macron = true;
                settings.syllabics = false;
                settings.cmro = false;
                if (sourceLanguageName === "nêhiyawêwin") {
                    setDictionaryName(process.env.REACT_APP_SRO_MACRONS_NAME);
                }
                setDispType("Latn-x-macron");
                break;
            case "Cans":
                settings.latn = false;
                settings.latn_x_macron = false;
                settings.syllabics = true;
                settings.cmro = false;
                if (sourceLanguageName === "nêhiyawêwin") {
                    setDictionaryName(process.env.REACT_APP_SYLLABICS_NAME);
                }
                setDispType("Cans");
                break;
            case "CMRO":
                settings.latn = false;
                settings.latn_x_macron = false;
                settings.syllabics = false;
                settings.cmro = true;
                setDispType("CMRO");
                break;
            case "ENGLISH":
                settings.label = "ENGLISH";
                break;
            case "LINGUISTIC (LONG)":
                settings.label = "LINGUISTIC (LONG)";
                break;
            case "LINGUISTIC (SHORT)":
                settings.label = "LINGUISTIC (SHORT)";
                break;
            case "NÊHIYAWÊWIN":
                settings.label = "NÊHIYAWÊWIN";
                break;
            case "TSUUT'INA":
                settings.label = "TSUUT'INA";
                break;
            case "X̲AAD KÍL":
                settings.label = "X̲AAD KÍL";
                break;
            case "HINÓNO'ÉÍ":
                settings.label = "HINÓNO'ÉÍ";
                break;
            default:
                break;
        }
        window.localStorage.setItem("settings", JSON.stringify(settings));
        window.dispatchEvent(new Event("settings"));
    };

    window.dispatchEvent(new Event("type"));

    window.onload = () => {
        updateDictionaryName();
    }

    window.onstorage = () => {
        // When local storage changes, dump the list to
        // the console.
        console.log(JSON.parse(window.localStorage.getItem("settings")));
    };

    const handleSearchKey = (e) => {
        if (e.key === "Enter") {
            setQuery(true);
        }
    };

    const handleSearchText = ({target}) => {
        setQueryString(target.value);
    };

    return (
        <div className="top-bar app__header">
            {window.location.href.includes("search") && (
                <>
                    <Redirect
                        to={{
                            pathname: "/search/?q=" + window.location.href.split("q=")[1],
                            state: {
                                queryString: window.location.href.split("q=")[1],
                                query: window.location.href.split("q=")[1],
                                type: type,
                            },
                        }}
                    ></Redirect>
                </>
            )}
            {window.location.href.includes("word") && (
                <>
                    <Redirect
                        to={{
                            pathname: "/word/" + window.location.href.split("/")[4],
                            state: {type: type}
                        }}
                    ></Redirect>
                </>
            )}
            {query ? (
                <Redirect
                    to={{
                        pathname: "/search/?q=" + queryString,
                        state: {
                            queryString: queryString,
                            query: query,
                            type: type,
                        },
                    }}
                ></Redirect>
            ) : null}

            <header className="branding top-bar__logo">
                <a className="branding__logo" href="/">
                    <img
                        className="branding__image"
                        src={morphodict_default_logo}
                        alt="mîkiwâhp (teepee) logo"
                    ></img>

                    <hgroup className="branding__text">
                        <h1 className="branding__heading branding__title">
                            {" "}
                            {dictionaryName}
                        </h1>
                        <p
                            className="branding__heading branding__subtitle"
                            role="doc-subtitle"
                        >
                            {description}
                        </p>
                    </hgroup>
                </a>
            </header>
            <nav className="search top-bar__search">
                <TextField
                    id="search"
                    variant="outlined"
                    fullWidth
                    label="Search"
                    onKeyUp={handleSearchKey}
                    onChange={handleSearchText}
                ></TextField>
            </nav>
            <nav className="top-bar__nav">
                <details className="toggle-box toggle-box--with-menu close-on-click-away">
                    <summary
                        id="settings-menu__button"
                        className="toggle-box__toggle"
                        data-cy="settings-menu"
                        aria-haspopup="menu"
                        tabIndex="0"
                    >
                        Settings
                    </summary>

                    <div
                        className="menu toggle-box__menu"
                        aria-labelledby="settings-menu__button"
                    >
                        <div className="menu__category">
                            <h3 className="menu__header">
                                Show {sourceLanguageName} words in…
                            </h3>
                            <ul className="menu__choices" data-cy="orthography-choices">
                                {/* list of setting menu */}
                                {Object.keys(settingMenu).map((id, index) => (
                                    <li className="menu-choice" key={index}>
                                        <button
                                            data-orth-switch
                                            value={id}
                                            className="unbutton fill-width"
                                            onClick={() => handleSettingChange(id)}
                                        >
                      <span className="menu-choice__label">
                        {settingMenu[id]}
                      </span>
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <hr className="menu__separator"></hr>

                        <div className="menu__category">
                            <a
                                href="/settings"
                                className="menu-choice"
                                data-cy="settings-link"
                            >
                <span className="menu-choice__label fill-width">
                  View all settings
                </span>
                            </a>
                        </div>
                    </div>
                </details>
            </nav>
        </div>
    );
}

export default Header;
