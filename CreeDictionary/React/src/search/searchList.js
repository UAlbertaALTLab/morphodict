/*
* SearchList class
*
*   - Returns list format of result of searched word
*   - Fetch on DisplayWords when onClick on listed words 
*/

import React from 'react';

import { wordDetail } from '../util';
import { reset2 } from '../detail/detailWords';

import DetailWords from "../detail/detailWords";

import PropTypes from "prop-types";

var loaded = false;

//Boolean function for to render DetailWords
export const reset = () => {
    loaded = false;
}

class SearchList extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            det: null,
            lem: null,
            A: null,
            word: null,
        };
    }

    /*  
    * Used when user onClicks on word listed
    * Fetch the word user onClicked
    * Sets responce to state.det 
    */
    detail(item) {
        //alert(item);
        loaded = true;
        reset2();
        this.setState({
            word: item,
        })
        wordDetail(item).then(response => {
            console.log(response)
            response.json().then(data => {
                //console.log(JSON.stringify(data))
                this.setState({
                    det: data.inflections,
                    lem: data.lemma,
                }, () => console.log(this.state))
            })
        })
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

    //render
    render(props) {
        // While loadind data
        if (!this.props.Words) {
            return (<div></div>);
        }
        // Returns list of result
        if (this.props.Words && !loaded) {
            if (this.isEmpty(this.props.Words) === true) {
                return (
                    <div className="container">
                        <section>
                            <h1>No Result</h1>
                        </section>
                    </div>
                );
                }
            return (
                <div className="form-row">
                    <section>
                        <ul className="list">
                            {this.props.Words.map((wordlist) => {
                                return <li key={wordlist.id} onClick={() => this.detail(wordlist.context)}>{wordlist.context} | {this.language(wordlist.language)} | {this.lcategory(wordlist.type)}</li>
                            })
                            }
                        </ul>
                    </section>
                </div>
            );
        }
        // When onClicked and fetched data loaded
        if (this.props.Words && loaded) {
            return (
                    <DetailWords
                        det={this.state.det}
                        word={this.state.word}
                        lem = {this.state.lem}>
                    </DetailWords>
            );
        }
        return (<div><h1>Error page</h1></div>);
    }
    
}

export default SearchList;
