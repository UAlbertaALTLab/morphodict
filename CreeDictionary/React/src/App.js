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

import { Route, HashRouter, BrowserRouter} from "react-router-dom";

class App extends Component {

    //render
    render() {
        console.log("Route: "+Route);
        return (
            <HashRouter>
            <div className="card-body">
                <header>
                    <h1>Dictionary</h1>
                </header>
                <Route exact component={SearchForm}/>
                <Route path="/search" component={SearchList}/>
                <Route path="/definition" component={DetailWords}/>
            </div>
            </HashRouter>
        );
    }
}

export default App;
