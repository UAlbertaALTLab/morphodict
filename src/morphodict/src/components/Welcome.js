import MainPageCrk from "./crkeng/MainPage";
import MainPageSrs from "./srseng/MainPage";
let MainPage = import("./DefaultWelcomePage");

function Welcome(props) {
  const title = process.env.REACT_APP_NAME
  const description = process.env.REACT_APP_SUBTITLE
  const endonym = process.env.REACT_APP_SOURCE_LANGUAGE_ENDONYM

  return (
        <div>
          <article className="prose box">
            <h2 className="prose__heading no-italics">tânisi!</h2>

            <p>{title} is a {description}.</p>
            {endonym === "Tsuut'ina" ? <MainPageSrs /> :
            endonym === "nêhiyawêwin" ? <MainPageCrk /> :
            <MainPage/> }

          </article>
        </div>
    );
}

export default Welcome;
