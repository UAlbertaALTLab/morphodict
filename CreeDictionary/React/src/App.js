/*
* App Class
*   
*   Returns top page when first load page
*/

import React, { Component } from 'react';
import './App.css';

import SearchForm from './search/searchForm';

class App extends Component {

    //render
    render() {
        return (
            <div className="App">
                <header className="App-header-text">
                    <h1>Dictionary</h1>
                </header>
                <div>
                    <SearchForm />
                </div>
            </div>
        );
    }
}

export default App;
