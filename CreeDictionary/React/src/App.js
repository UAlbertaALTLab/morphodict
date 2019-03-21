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

import { Route, HashRouter, BrowserRouter } from "react-router-dom";

class App extends Component {

    //render
    render() {
        console.log("Route: " + Route);
        return (
            <HashRouter>
                <div className="wrapper">
                    <div className="main-panel">
                        <div className="content">
                            <div className="row">
                                <div className="col-12">
                                    <div className="card">
                                        <header className="card-header">
                                            <h1 className="card-title">Dictionary</h1>
                                        </header>
                                        <Route exact component={SearchForm} />
                                        <Route path="/search" component={SearchList} />
                                    </div>
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
