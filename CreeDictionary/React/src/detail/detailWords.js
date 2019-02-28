/*
* DetailWords class
*
*   Returns table fomat of Word detail of clicked word in SearchList
*/

import React from 'react';

import './detailWords.css';

class DetailWords extends React.Component {

    //renders
    render(props) {
        console.log('Detail: ' + JSON.stringify(this.props.det));

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

        //returns in Table Format
        return (
            <div className="detaildiv">
                <section>
                    <h1>{this.props.word}</h1>
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