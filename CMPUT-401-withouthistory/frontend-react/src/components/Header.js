import "./style.css";
import morphodict_default_logo from "../static/morphodict-default-logo-192.png";

import React, { useState } from "react";
import { TextField } from "@mui/material";
import { Redirect } from "react-router-dom";
import Settings from "../HelperClasses/SettingClass";

function Header(props) {
  const [dictionaryName, setDictionaryName] = useState("itwêwina");
  const [sourceLanguageName, setSourceLanguageName] = useState("Plains Cree");
  const [queryString, setQueryString] = useState("");
  const [query, setQuery] = useState(false);
  const [type, setDispType] = useState("Latn");
  const [settingMenu, setSettingMenu] = useState({
    Latn: "SRO (êîôâ)",
    "Latn-x-macron": "SRO (ēīōā)",
    Cans: "Syllabics",
    ENGLISH: "English Labels", 
    "LINGUISTIC (LONG)": "Linguistic Labels (long)", 
    "LINGUISTIC (SHORT)": "Linguistic Labels (short)",
    NÊHIYAWÊWIN: "nêhiyawêwin labels",
  });

  if (!window.localStorage.getItem("settings")) {
    window.localStorage.setItem("settings", JSON.stringify(new Settings()));
  }

  const handleSettingChange = (value) => {
    let settings = JSON.parse(window.localStorage.getItem("settings"));

    switch (value) {
      case "Latn":
        settings.latn = true;
        settings.latn_x_macron = false;
        settings.syllabics = false;
        setDispType("Latn");
        break;
      case "Latn-x-macron":
        settings.latn = false;
        settings.latn_x_macron = true;
        settings.syllabics = false;
        setDispType("Latn-x-macron");
        break;
      case "Cans":
        settings.latn = false;
        settings.latn_x_macron = false;
        settings.syllabics = true;
        setDispType("Cans");
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
      default:
        break;
    }
    window.localStorage.setItem("settings", JSON.stringify(settings));
    window.dispatchEvent(new Event("settings"));
  };

  window.dispatchEvent(new Event("type"));

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

  const handleSearchText = ({ target }) => {
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
              {sourceLanguageName} Dictionary
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
                href="/cree-dictionary-settings"
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
