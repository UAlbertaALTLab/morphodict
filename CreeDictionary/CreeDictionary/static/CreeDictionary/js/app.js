

function load_results(query_string){
    let instruction_text = document.getElementById("instruction-text");
    let loading_cards = document.getElementsByClassName("title-row-container loading-title-row");
    console.log(loading_cards);

    if (query_string !== ""){
        document.getElementById("search-results").innerHTML = "";
        window.history.replaceState(query_string, "", "/cree-dictionary/search/"+query_string + '/');

        // document.getElementById("instruction-text").innerHTML = val;


        let hidden_att = document.createAttribute("hidden");
        instruction_text.setAttributeNode(hidden_att);



        let hint_text = document.getElementsByClassName("hint-text");
        hint_text[0].removeAttribute('hidden');

        let searching_word = document.getElementById("searching-word");
        searching_word.innerText = query_string;


        let i;
        for (i=0; i<loading_cards.length; i++){
            loading_cards[i].removeAttribute("hidden");
        }

        let xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState === 4 && this.status === 200) {
                const inputNow = document.getElementById("search-input").value;
                if (inputNow === query_string){
                    document.getElementById("search-results").innerHTML = this.responseText;
                    for (i=0; i<loading_cards.length; i++){
                        let hidden_att = document.createAttribute("hidden");
                        loading_cards[i].setAttributeNode(hidden_att);

                    }


                }
            }
        };

        // url is hardcoded, future change to the url needs to be updated here
        xhttp.open("GET", "/cree-dictionary/cree-dictionary/_search/" + query_string + "?render-html=true/", true);
        xhttp.send();



    }
    else{
        let hint_text = document.getElementsByClassName("hint-text");
        let hint_hidden_att = document.createAttribute("hidden");
        hint_text[0].setAttributeNode(hint_hidden_att);

        document.getElementById("search-results").innerHTML = "";
        window.history.replaceState(query_string, "", "/cree-dictionary/");
        instruction_text.removeAttribute("hidden");

        let i;
        for (i=0; i<loading_cards.length; i++){
            let hidden_att = document.createAttribute("hidden");
            loading_cards[i].setAttributeNode(hidden_att);
        }


    }


}