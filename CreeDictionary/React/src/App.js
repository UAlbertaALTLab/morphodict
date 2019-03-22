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

import { Route, HashRouter, BrowserRouter, Link } from "react-router-dom";

class App extends Component {

    //render
    render() {
        console.log("Route: " + Route);
        return (
            <HashRouter>
                <div className="wrapper">
                    <div className="sidebar" data-color="orange">
                        <div className="sidebar-wrapper">
                            <section className="nav">
                                <li className="active" >
                                <a href="/">Back to the top</a>
                                </li>
                            </section>
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
