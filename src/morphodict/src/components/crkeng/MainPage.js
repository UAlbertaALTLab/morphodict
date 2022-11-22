function MainPageCrk() {
  const long_word = "ê-kî-nitawi-kâh-kîmôci-kotiskâwêyâhk";
    return (
        <div>
            <p>
                Type any Cree word to find its English translation. You can search for
                short Cree words (e.g., <a href={
                `/word/atim`
            }

            > atim</a>) or very long
                Cree words (e.g.,
                {
                    " "
                }
                <a data-cy="long-word-example" href={`/search/?q=${long_word}`}>
                    {long_word}
                </a>
                ). Or you can type an English word and find its possible Cree
                translations. You can write words in Cree using standard Roman
                orthography (SRO) (e.g.,
                {
                    " "
                }
                <a href="/word/acimosis">
                    <span lang="cr">acimosis</span>
                </a>
                ) or using syllabics (e.g.,
                {
                    " "
                }
                <a href="/word/ᐊᒋᒧᓯᐢ">
                    <span lang="cr">ᐊᒋᒧᓯᐢ</span>
                </a>
                ).
            </p>

            <p>
                <a href="/words/itwêwina">itwêwina</a> was made by the{" "}
                <a href="https://altlab.artsrn.ualberta.ca/">
                    Alberta Language Technology Lab (ALTLab)
                </a>
                , in collaboration with the{" "}
                <a href="https://www.fnuniv.ca/">First Nations University</a> and{" "}
                <a href="https://www.maskwacised.ca/">
                    Maskwacîs Education Schools Commission (MESC)
                </a>
                . The dictionary entries are courtesy of{" "}
                <a href="https://www.fnuniv.ca/academic/faculty/dr-arok-wolvengrey/">
                    Dr. Arok Wolvengrey
                </a>
                and MESC.
            </p>

            <p>
                The spoken Cree word recordings are courtesy of{" "}
                <a href="https://speech-db.altlab.app/maskwacis/speakers/">
                    speakers in Maskwacîs
                </a>
                .
            </p>
        </div>
    );
}

export default MainPageCrk;
