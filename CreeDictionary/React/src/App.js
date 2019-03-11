/*
* App Class
*   
*   Returns top page when first load page
*/

import React, { Component } from 'react';

import SearchForm from './search/searchForm';

class App extends Component {

    //render
    render() {
        return (
            <div className="container">
                <header>
                    <h1>Dictionary</h1>
                </header>
                <SearchForm />
            </div>
        );
    }
}

export default App;
