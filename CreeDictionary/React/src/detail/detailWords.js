/*
* DetailWords class
*
*   Returns table fomat of Word detail of clicked word in SearchList
*/

import React from 'react';

import { wordDetail } from '../util';
import { withRouter } from 'react-router-dom';

class DetailWords extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            inflection: null,
            lemma: null,
            definition: null,
        };
    }

    //Search word again from table , for sprint 4
    //Add onClick={() => this.reSearch(key[1]) in <td className="td-actions text-left" key={key}>{key[1]}</td>
    reSearch(item) {
        event.preventDefault();
        this.props.history.push('/search/' + item);
    }

    isEmpty(obj) {
        for (var key in obj) {
            if (obj.hasOwnProperty(key))
                return false;
        }
        return true;
    }

    gainDetail() {
        //alert(item);
        wordDetail(this.props.location.pathname.split('/')[2]).then(response => {
            console.log(response)
            response.json().then(data => {
                //console.log(JSON.stringify(data))
                this.setState({
                    inflection: data.inflections,
                    lemma: data.lemma,
                    definition: data.lemma.definitions,
                }, () => console.log(this.state))
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
            this.gainDetail();
        }
    }

    componentDidMount() {
        this.gainDetail()
        console.log('called2');
    }

    //renders
    render() {
        console.log('Path : ' + this.props.location.pathname.split('/')[2]);
        if ((this.isEmpty(this.state.inflection) === true) && (this.isEmpty(this.state.definition) === false)) {
            return (
                <div className="row">
                    <div className="col-12">
                        <section>
                            <h1>{this.props.location.pathname.split('/')[2]}</h1>
                        </section>
                        <div className="card">
                            <div className="card-header">
                                <h2 className="card-title">Definition</h2>
                            </div>
                            <section className="card-body">
                                {this.state.definition.map((e) => {
                                    return (
                                        <h3 key={e.id} className="text-center" >{e.context}<br /><sub>{e.source}</sub></h3>)
                                })}
                            </section>
                        </div>
                    </div>
                </div>
            );
        }
        else if ((this.isEmpty(this.state.inflection) === false) && ((this.isEmpty(this.state.definition) === false))) {
            return (
                <div className="row">
                    <div className="col-12">
                        <section>
                            <h1>{this.props.location.pathname.split('/')[2]}</h1>
                        </section>
                        <div className="card">
                            <div className="card-header">
                                <h2 className="card-title">Definition</h2>
                            </div>
                            <section className="card-body">
                                {this.state.definition.map((e) => {
                                    return (
                                        <h3 key={e.id}>{e.context}<br /><sub>{e.source}</sub></h3>)
                                })}
                            </section>
                        </div>
                        <div className="table-responsive">
                            <table className="table">
                                <thead>
                                    <tr>
                                        {Object.entries(this.state.inflection[0]).map((key, val) => <th className="text-center" key={key}>{key[0]}</th>)}
                                    </tr>
                                </thead>
                                <tbody>
                                    {this.state.inflection.map(e => (
                                        <tr key={e.id}>
                                            {Object.entries(e).map((key, val) => {
                                                if (key[0] === "inflectionForms") {
                                                    return <td className="text-left" key={key}>Object</td>
                                                }
                                                if (key[0] === "context") {
                                                    return <td className="td-actions text-left" key={key}>{key[1]}</td>
                                                }
                                                if (key[0] === "definitions") {
                                                    return <td className="td-actions text-left" key={key}>def</td>
                                                }
                                                return <td className="text-left" key={key}>{key[1]}</td>
                                            })
                                            }
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

            );
        }
        else {
            return (<div><h1>{this.props.location.pathname.split('/')[2]}</h1></div>)
        }
    }
}

export default withRouter(DetailWords);
