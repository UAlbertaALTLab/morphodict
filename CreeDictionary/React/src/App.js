/*
* App Class
*   
*   Returns top page when first load page
*/

import React, { Component } from 'react';

import SearchForm from './search/searchForm';
import SearchList from './search/searchList';
import DetailWords from './detail/detailWords';

//import { Router, Route, Switch } from "react-router";
//import { TranslatorProvider, useTranslate, translate} from "react-translate"
//import { setTranslations, setDefaultLanguage, translate } from 'react-multi-lang'
/*import { IntlProvider, FormattedMessage, addLocaleData} from 'react-intl'
import ja from "react-intl/locale-data/ja";
addLocaleData([...ja]);

import { LocalizeProvider } from "react-localize-redux";*/

import { Route, HashRouter, BrowserRouter, Link } from "react-router-dom";
import i18next from "./i8next";

export var cree=false;

class App extends Component {

    /*constructor(prop) {
        super(prop);
        this.state = {
          locale: 'ja',
          message: {
              "Hello": "こんにちは"},// 実際のメッセージファイル
        }
      }
        <p>
            <FormattedMessage id="Hello" defaultMessage="It's a beautiful day outside." />
        </p>
      */
    

    translate(){
        cree = !cree;
        if (cree === true){
            i18next.changeLanguage("en");
        }else{
            i18next.changeLanguage("ja");
        }
    }

    //render
    render() {
        console.log("AAAAAA: "+i18next.language);
        console.log("BBBBBB: "+i18next.languages);
        if (cree === true){
            i18next.changeLanguage("en");
            console.log("CCCCC: "+i18next.language);
        }else{
            i18next.changeLanguage("ja");
        }
        return (
            <HashRouter>
                <div className="wrapper">
                    <div className="sidebar" data-color="green">
                        <div className="sidebar-wrapper">
                            <section className="nav">
                                <li>
                                <a href="/">Back to the top</a>
                                </li>
                                <li>
                                <a onClick={()=>this.translate()}>Cree</a>
                                </li>
                            </section>
                            <p>{i18next.t('hello')}
                            </p>
                        </div>
                    </div>
                    <div className="main-panel">
                        <nav className="navbar navbar-expanded-lg navbar-absolute navbar-transparent">
                            <div className="container-fluid">
                                <div className="navbar-wrapper">
                                    <div className="navbar-toggle d-inline">
                                        <button type="button" className="navbar-toggler">
                                            <span className="navbar-toggler-bar bar1"></span>
                                            <span className="navbar-toggler-bar bar2"></span>
                                            <span className="navbar-toggler-bar bar3"></span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </nav>
                        <div className="content">
                            <div className="row">
                                <div className="col-12">
                                    <div className="card">
                                        <header className="card-header">
                                            <h1 className="card-title">Dictionary</h1>
                                        </header>
                                        <Route exact component={SearchForm} />
                                    </div>
                                    <Route path="/search" component={SearchList} />
                                    <Route path="/definition" component={DetailWords} />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </HashRouter>
        );
    }
}

export default App;
