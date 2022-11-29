import "./style.css";

function Footer(props) {
    const handleModeChange = (value) => {
        let settings = JSON.parse(window.localStorage.getItem("settings"));

        switch (value) {
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

    const endonym = process.env.REACT_APP_SOURCE_LANGUAGE_ENDONYM;
    const sourceLanguageName = process.env.REACT_APP_SOURCE_LANGUAGE;

    return (
        <footer className="footer app__footer">
            <ul className="footer__links footer__basic-links ">
                <li>
                    <a
                        href="http://altlab.artsrn.ualberta.ca/itwewina#help"
                        className="footer-links__link"
                        target="_blank"
                        rel="noopener"
                    >
                        Help
                    </a>
                </li>
                {/* if MORPHODICT_DICTIONARY_NAME == "itwêwina" */}
                {/* <li><a href="url 'cree-dictionary-legend'" className="footer-links__link">Legend of abbreviations</a></li> */}
                {/* endif */}
                <li>
                    <a href="/cree-dictionary-legend" className="footer-links__link">
                        Legend of abbreviations
                    </a>
                </li>
                <li>
                    <a href="/about" className="footer-links__link">
                        About
                    </a>
                </li>
                <li>
                    <a href="/contact-us" className="footer-links__link">
                        Contact us
                    </a>
                </li>
            </ul>

            <div className="footer__links footer__advanced-links">
                <ul className="footer__links">
                    <li>
                        <a href="/settings" className="footer-links__link">
                            Settings
                        </a>
                    </li>
                </ul>

                <h2 className="footer__option-header"> View search results in: </h2>
                <ul className="unbullet">
                    <li>
                        <button
                            className="unbutton link footer__link"
                            type="submit"
                            name="mode"
                            value="community"
                            data-cy="enable-community-mode"
                            onClick={() => handleModeChange("ENGLISH")}
                        >
                            Plain English mode
                        </button>
                    </li>
                    <li>
                        <button
                            className="unbutton link footer__link"
                            type="submit"
                            name="mode"
                            value="linguistic"
                            data-cy="enable-linguistic-mode-short"
                            onClick={() => {
                                handleModeChange("LINGUISTIC (SHORT)");
                            }}
                        >
                            Linguist mode (short)
                        </button>
                    </li>
                    <li>
                        <button
                            className="unbutton link footer__link"
                            type="submit"
                            name="mode"
                            value="linguistic"
                            data-cy="enable-linguistic-mode-long"
                            onClick={() => {
                                handleModeChange("LINGUISTIC (LONG)");
                            }}
                        >
                            Linguist mode (long)
                        </button>
                    </li>
                    <li>
                        <button
                            className="unbutton link footer__link"
                            name="mode"
                            value="linguistic"
                            data-cy="enable-source-language-mode"
                            onClick={() => {
                                handleModeChange(sourceLanguageName);
                            }}
                        >
                            {endonym} mode
                        </button>
                    </li>
                </ul>
            </div>

            <div className="footer__copyright copyright">
                <p className="copyright__line">
                    2019–{new Date().getFullYear()} © Alberta Language Technology Lab.
                </p>
                <p className="copyright__line">
                    {" "}
                    Modified icons copyright © 2019{" "}
                    <a href="https://github.com/FortAwesome/Font-Awesome/tree/5.11.1">
                        Font Awesome
                    </a>
                    , licensed under{" "}
                    <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.
                </p>
            </div>
        </footer>
    );
}

export default Footer;
