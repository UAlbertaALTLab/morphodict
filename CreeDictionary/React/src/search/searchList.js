/*
* SearchList class
*
*   - Returns list format of result of searched word
*   - Fetch on DisplayWords when onClick on listed words 
*/

import React from 'react';

import { withRouter } from 'react-router-dom';

import { searchWord } from '../util';

class SearchList extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            list: null,
        };
    }

    /*  
    * Used when user onClicks on word listed
    * Sends clicked word to history as path
    */
    click(word) {
        //alert(item);
        event.preventDefault();
        this.props.history.push('/definition/' + word);
    }

    //display language
    language(word) {
        if (word === "crk") {
            return "Cree"
        }
    }

    //display category
    lcategory(word) {
        if (word === "V") {
            return "Verb"
        } else if (word === "N") {
            return "Noun"
        } else {
            return word
        }
    }

    //Checks if data is empty
    isEmpty(obj) {
        for (var key in obj) {
            if (obj.hasOwnProperty(key))
                return false;
        }
        return true;
    }

    // returns word in path of current path(location)
    getWord() {
        const word = this.props.location.pathname.split('/')[2];
        return word
    }

    // Fetches on searching word 
    // set list to returned data
    gainList() {
        //alert(item);
        searchWord(this.props.location.pathname.split('/')[2]).then(response => {
            console.log(response)
            response.json().then(data => {
                //console.log(JSON.stringify(data))
                this.setState({
                    list: data.words,
                }, () => console.log(this.state))
            })
        })
        return this.state.list
    }

    // Checks if the searchoing word changed, if it is reload(reRender)
    componentDidUpdate(prevProps) {
        // Typical usage (don't forget to compare props):
        if (this.props.location.pathname.split('/')[2] !== prevProps.location.pathname.split('/')[2]) {
            //alert('its dif');
            this.gainList();
        }
    }

    // Checks if componenet did mount
    componentDidMount() {
        this.gainList()
        console.log('called');
    }

    //render
    render() {
        //console.log(this.state.list);
        //console.log(this.props.location.pathname.split('/'));
        /*If data not loaded */
        if (this.isEmpty(this.state.list) === true && this.state.list !== null) {
            return (<div><h2>No Result</h2></div>)
        }
        else if (this.state.list === null){
            return (<div><p>Loading...</p></div>)
        }
        /* If data loaded*/
        else {
            return (
                <div className="row">
                    <div className="col-12">
                        {this.state.list.map((wordlist) => {
                            return (
                                <div key={wordlist.id} onClick={() => this.click(wordlist.context)} className="card">
                                    <h4 className="card-header">{wordlist.context}</h4>
                                    <p className="card-body">{this.language(wordlist.language)} | {this.lcategory(wordlist.type)}<br/>
                                    </p>
                                </div>
                            )
                        })
                        }
                    </div>
                </div>
            );
        }
    }

}

export default withRouter(SearchList);
