/*
* App Class
*   
*   Returns top page when first load page
*/

import React, { Component } from 'react';

import SearchForm from './components/search/searchForm';
import SearchResult from './components/search/searchResult';
import DetailWords from './components/detail/detailWords';
import NavSideBar from './components/navigation/navSideBar';
import NavNavBar from './components/navigation/navNavBar';

//import { Router, Route, Switch } from "react-router";
//import { TranslatorProvider, useTranslate, translate} from "react-translate"
//import { setTranslations, setDefaultLanguage, translate } from 'react-multi-lang'
/*import { IntlProvider, FormattedMessage, addLocaleData} from 'react-intl'
import ja from "react-intl/locale-data/ja";
addLocaleData([...ja]);

import { LocalizeProvider } from "react-localize-redux";*/

import { Route, HashRouter, BrowserRouter, Link } from "react-router-dom";
import i18next from "./utils/translate";

export var cree = false;

class App extends Component {

    //render
    render() {
        return (
            <HashRouter>
                <div className="wrapper">
                    <NavSideBar />
                    <div className="main-panel">
                        <NavNavBar />
                        <div className="content">
                            <div className="row">
                                <div className="col-12">
                                    <div className="card">
                                        <header className="card-header">
                                            <h1 className="card-title">{i18next.t('Dictionary')}</h1>
                                        </header>
                                        <Route exact component={SearchForm} />
                                    </div>
                                    <Route path="/search" component={SearchResult} />
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
