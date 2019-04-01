/*
* App Class
*   
*   Returns top page when first load page
*/

import React, { Component } from 'react';

import SearchForm from './search/searchForm';
import SearchList from './search/searchList';
import DetailWords from './detail/detailWords';
import NavSideBar from './navigation/navSideBar';
import NavNavBar from './navigation/navNavBar';

//import { Router, Route, Switch } from "react-router";
//import { TranslatorProvider, useTranslate, translate} from "react-translate"
//import { setTranslations, setDefaultLanguage, translate } from 'react-multi-lang'
/*import { IntlProvider, FormattedMessage, addLocaleData} from 'react-intl'
import ja from "react-intl/locale-data/ja";
addLocaleData([...ja]);

import { LocalizeProvider } from "react-localize-redux";*/

import { Route, HashRouter, BrowserRouter, Link } from "react-router-dom";
import i18next from "./translate";

export var cree=false;

class App extends Component {

    //render
    render() {
        return (
            <HashRouter>
                <div className="wrapper">
                    <div className="sidebar">
                        <NavSideBar/>
                    </div>
                    <div className="main-panel">
                        <nav className="navbar navbar-expanded-lg navbar-absolute navbar-transparent">
                            <NavNavBar/>
                        </nav>
                        <div className="content">
                            <div className="row">
                                <div className="col-12">
                                    <div className="card">
                                        <header className="card-header">
                                            <h1 className="card-title">{i18next.t('Dictionary')}</h1>
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
