import MainPageCrk from "./crkeng/MainPage";
import MainPageSrs from "./srseng/MainPage";
import MainPageArp from "./arpeng/MainPage";
import MainPageCwd from "./cwdeng/MainPage";
import MainPageHdn from "./hdneng/MainPage";
let MainPage = import("./DefaultWelcomePage");

function Welcome(props) {
  const title = process.env.REACT_APP_NAME
  const description = process.env.REACT_APP_SUBTITLE
  const endonym = process.env.REACT_APP_SOURCE_LANGUAGE_ENDONYM
  const welcome = process.env.REACT_APP_WELCOME

  return (
        <div>
          <article className="prose box">
            <h2 className="prose__heading no-italics">{welcome}</h2>

            <p>{title} is a {description}.</p>
            {endonym === "Tsuut'ina" ? <MainPageSrs /> :
            endonym === "nêhiyawêwin" ? <MainPageCrk /> :
            endonym === "Hinónoʼeitíít" ? <MainPageArp /> :
            endonym === "nîhithawîwin" ? <MainPageCwd /> :
            endonym === "X̲aad Kíl" ? <MainPageHdn /> :
            <MainPage/> }

          </article>
        </div>
    );
}

export default Welcome;
