/*
* DetailWords class
*
*   Returns table fomat of Word detail of clicked word in SearchList
*/

import React from 'react';

import './detailWords.css';
import SearchList from '../search/searchList';

import { reset } from '../search/searchList';
import { searchWord } from '../util';

var sended = false;

export const reset2 = () => {
    sended = false;
}

class DetailWords extends React.Component {

    constructor(props) {
        super(props);
        this.Words = null;
      }

    reSearch(item) {
        sended = true;
        reset();
        searchWord(item).then(response => {
            console.log(response)
            response.json().then(data => {
              //console.log(JSON.stringify(data))
              this.setState({
                Words: data.words,
              }, () => console.log(this.state))
            })
        });
    }

    //renders
    render(props) {
        console.log('Detail: ' + JSON.stringify(this.props.det));
        console.log('lemma: ' + JSON.stringify(this.props.lem));
        //While loading data returns below 
        if (!this.props.det) {
            return (
                <div className="detaildiv">
                    <section>
                        <h1>{this.props.word}</h1>
                    </section>
                </div>
            );
        }

        if (sended===true){
            return (
            <SearchList
                Words={this.state.Words}>
            </SearchList>
            );
        }
        //returns in Table Format
        return (
            <div className="detaildiv">
                <section>
                    <h1>{this.props.word}</h1>
                </section>
                <section>
                {this.props.lem.definitions.map(e => (<p key={e.id}>{e.context}</p>))}
                </section>
                <table>
                    <thead>
                        <tr>
                            {Object.entries(this.props.det[0]).map((key, val) => <th key={key}>{key[0]}</th>)}
                        </tr>
                    </thead>
                    <tbody>
                        {this.props.det.map(e => (
                            <tr key={e.id}>
                                {Object.entries(e).map((key, val) => {
                                    if (key[0] === "inflectionForms") {
                                        return <td key={key}>Object</td>
                                    }
                                    if (key[0] === "context"){
                                        return <td key={key} onClick={() => this.reSearch(key[1])}>{key[1]}</td>
                                    }
                                    return <td key={key}>{key[1]}</td>
                                })
                                }
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
        }
    }

export default DetailWords;

/* Please ignore
return (
            <div className="centre">
                <div>
                    <h1>{this.props.word}</h1>
                </div>
                <section>
                    <ul className="centreli">
                        {this.props.det.map((wordlist) => {
                                return <li key={wordlist.id}>{wordlist.context}</li>
                            })
                        }
                    </ul>
                </section>
            </div>
        );
*/