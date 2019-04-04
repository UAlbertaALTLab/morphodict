/*
* SearchList class
*
*   - Returns list format of result of searched word
*   - Fetch on DisplayWords when onClick on listed words 
*/

import React from 'react';

import { withRouter } from 'react-router-dom';
import i18next from '../../utils/translate';

import { searchWord } from '../../utils/network';
import ResultDetail from './resultDetail';

class SearchResult extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            list: null,
            analysis: null,
        };
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

    getAnalysis() {
        if (this.isEmpty(this.state.analysis) === true) {
            return (<p></p>);
        } else {
            return (
                <div className="card">
                    <h3 className="card-header card-title">{i18next.t('LinguisticAnalysis')}</h3>
                    <h4 className="card-body text-center">{this.state.analysis.join("")}</h4>
                </div>
            )
        }
    }

    // Fetches on searching word 
    // set list to returned data
    gainList() {
        //alert(item);
        searchWord(this.props.location.pathname.split('/')[2]).then(response => {
            //console.log(response.status)
            if (response.status === 500) {
                this.setState({
                    list: [],
                }, () => console.log(this.state))
                return (console.log('Error'))
            }
            response.json().then(data => {
                //console.log(JSON.stringify(data))
                this.setState({
                    list: data.words,
                    analysis: data.analysis,
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
            return (
                <div className="row">
                    <div className="col-lg-9">
                        <div className="card">
                            <div className="card-header">
                                <h2 className="card-title">{i18next.t('NoResult')}</h2>
                            </div>
                        </div>
                    </div>
                </div>
            )
        }
        else if (this.state.list === null) {
            return (
                <div>
                    <div className="col-lg-9">
                        <div className="card">
                            <div className="card-header">
                                <p className="card-title">{i18next.t('Loading')}</p>
                            </div>
                        </div>
                    </div>
                </div>
            )
        }
        /* If data loaded*/
        else {
            return (
                <div className="row flex-lg-row-reverse">
                    <div className="col-lg-3">
                        {this.getAnalysis()}
                    </div>
                    <div className="col-lg-9">
                        {this.state.list.map((wordlist, index) => {
                            return (
                                <ResultDetail
                                    key={wordlist.id}
                                    id={wordlist.id}
                                    word={wordlist.context}
                                    definition={wordlist.definitions}
                                    type={wordlist.type}
                                    language={wordlist.language}
                                    wordlist={wordlist}
                                />
                            )
                        })
                        }
                    </div>
                </div>
            );
        }
    }

}

export default withRouter(SearchResult);
