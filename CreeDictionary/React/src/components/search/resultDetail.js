import React from 'react';

import { withRouter } from 'react-router-dom';
import i18next from '../../utils/translate';

class ResultDetail extends React.Component {

    /*  
    * Used when user onClicks on word listed
    * Sends clicked word to history as path
    */
    click(word) {
        //alert(item);
        event.preventDefault();
        this.props.history.push('/definition/' + word);
    }

    //Checks if data is empty
    isEmpty(obj) {
        for (var key in obj) {
            if (obj.hasOwnProperty(key))
                return false;
        }
        return true;
    }

    //display language
    language(word) {
        if (word === "crk") {
            return i18next.t('Cree')
        } else if (word === "eng") {
            return i18next.t('Eng')
        } else {
            return word
        }
    }

    //display category
    lcategory(word) {
        if (word === "V") {
            return i18next.t('Verb')
        } else if (word === "N") {
            return i18next.t('Noun')
        } else if (word === "Ipc") {
            return i18next.t('Ipc')
        } else {
            return word
        }
    }

    getdefinition(definition) {
        console.log("A " + definition)
        if (this.isEmpty(definition) === false) {
            return (<p>{definition.map((e) => {
                return (
                    <strong key={e.id}>{e.context}<br /><sub>{e.source}</sub><br /></strong>)
            })}</p>)
        }
        return (<p></p>)

    }

    render() {
        return (
            <div key={this.props.id} onClick={() => this.click(this.props.word)} className="card">
                <div className="card-header">
                    <div className="row">
                        <div className="col-sm-6 text-left">
                            <h3 className="card-title">{this.props.word}</h3>
                        </div>
                        <div className="col-sm-6 text-right">
                            <p>nan</p>
                        </div>
                    </div>
                </div>
                <section className="card-body">
                    <p>{this.language(this.props.language)} | {this.lcategory(this.props.type)}<br /></p>
                    {this.getdefinition(this.props.definition)}
                </section>
            </div>
        );
    }
}

export default withRouter(ResultDetail);