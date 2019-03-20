/*
* SearchList class
*
*   - Returns list format of result of searched word
*   - Fetch on DisplayWords when onClick on listed words 
*/

import React from 'react';

import { withRouter} from 'react-router-dom';

import { searchWord } from '../util';

var loaded = false;

//Boolean function for to render DetailWords
export const reset = () => {
    loaded = false;
}

class SearchList extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            list: null,
            recieved: "aaa",
        };
    }

    /*  
    * Used when user onClicks on word listed
    * Fetch the word user onClicked
    * Sets responce to state.det 
    */
    click(word) {
        //alert(item);
        event.preventDefault();
        this.props.history.push('/definition/'+word);
    }

	//display language
    language(word) {
    	if (word === "crk"){
    		return "Cree"
    	}
    }
    
    lcategory(word) {
    	if (word ==="V"){
    		return "Verb"
    	} else if (word === "N"){
    		return "Noun"
    	} else {
    		return word
    	}
    }

    isEmpty(obj) {
        for(var key in obj) {
            if(obj.hasOwnProperty(key))
                return false;
        }
        return true;
    }

    getWord(){
        const word = this.props.location.pathname.split('/')[2];
        return word
    }

    gainList() {
        //alert(item);
        searchWord(this.props.location.pathname.split('/')[2]).then(response => {
            console.log(response)
            response.json().then(data => {
                //console.log(JSON.stringify(data))
                this.setState({
                    list: data.words,
                    recieved: this.props.location.pathname.split('/')[2],
                }, () => console.log(this.state))
                loaded = true;
            })
        })
        return this.state.list
    }

    componentDidUpdate(prevProps) {
        console.log(this.isEmpty(prevProps));
        //console.log(prevprops.location.pathname.split('/'));
        // Typical usage (don't forget to compare props):
        if (this.props.location.pathname.split('/')[2] !== prevProps.location.pathname.split('/')[2]) {
          //alert('its dif');
          this.gainList();
        }
      }

    componentDidMount() {
        this.gainList()
        console.log('called');
    }

    //render
    render() {
        //console.log(this.gainList());
        console.log(this.props.location.pathname.split('/'));
        // While loadind data
        if (this.isEmpty(this.state.list) === true){
            return(<div><p>Loading...</p></div>)
        }
        else{
            return (
            <div className="form-row">
                <section>
                    <ul className="list">
                        {this.state.list.map((wordlist) => {
                            return <li key={wordlist.id} onClick={() => this.click(wordlist.context)}>{wordlist.context} | {this.language(wordlist.language)} | {this.lcategory(wordlist.type)}</li>
                        })
                        }
                    </ul>
                </section>
            </div>
        );
        }
    }
    
}

export default withRouter(SearchList);
