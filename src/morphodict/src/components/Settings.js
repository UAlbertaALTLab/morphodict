import CreeDictionarySettings from "./crkeng/CreeDictionarySettings";
import TsuutinaSettings from "./srseng/TsuutinaSettings";
import HaidaSettings from "./hdneng/HaidaSettings";
import ArapahoSettings from "./arpeng/ArapahoSettings";
import WoodsCreeSettings from "./cwdeng/WoodsCreeSettings";

function Settings(props) {
  const endonym = process.env.REACT_APP_SOURCE_LANGUAGE_ENDONYM

  return (
        <div>
            {endonym === "Tsuut'ina" ? <TsuutinaSettings /> :
            endonym === "nêhiyawêwin" ? <CreeDictionarySettings /> :
            endonym === "Hinónoʼeitíít" ? <ArapahoSettings /> :
            endonym === "nîhithawîwin" ? <WoodsCreeSettings /> :
            endonym === "X̲aad Kíl" ? <HaidaSettings /> :
            <CreeDictionarySettings /> }

        </div>
    );
}

export default Settings;
