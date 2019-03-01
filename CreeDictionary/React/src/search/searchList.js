/*
* SearchList class
*
*   - Returns list format of result of searched word
*   - Fetch on DisplayWords when onClick on listed words 
*/

import React from 'react';

import './searchList.css';

import { wordDetail } from '../util';

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
        this.setState({
            word: item,
        })
        wordDetail(item).then(response => {
            console.log(response)
            response.json().then(data => {
                //console.log(JSON.stringify(data))
                this.setState({
                    det: data.inflections,
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

    //render
    render(props) {
        // While loadind data
        if (!this.props.Words) {
            return (<div><h1>Loading...</h1></div>);
        }
        // Returns list of result
        if (this.props.Words && !loaded) {
            return (
                <div className="searchdiv">
                    <section>
                        <ul className="searchli">
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
                <div className="searchdiv">
                    <DetailWords
                        det={this.state.det}
                        word={this.state.word}>
                    </DetailWords>
                </div>
            );
        }
        return (<div><h1>Error page</h1></div>);
    }
    
}

export default SearchList;
