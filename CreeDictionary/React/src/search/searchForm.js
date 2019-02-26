import React from 'react';

import './searchForm.css';

import { searchWord, getLoaded } from '../util';

class SearchForm extends React.Component{
    state = {
        sended: false,
    };
    constructor(props) {
        super(props);
        this.state = {value: ''};
        this.data = [];

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
      }
    
      handleChange(event) {
        this.setState({value: event.target.value});
      }
    
      handleSubmit(event) {
        event.preventDefault();
        //const data = new FormData(event.target);
        this.setState({
            sended: true,
        });
        searchWord(this.state.value);
        if (getLoaded() === false) {
          alert('Word not sent');
          console.log(getLoaded());
        }
      }

      getClassNames() {
        let classNames = 'search';
        if (this.state.sended === true) {
          classNames += 'isTrue';
        }
        return classNames;
      }

    render() {
        return (
            <div>
            <form onSubmit={this.handleSubmit.bind(this)} className={this.getClassNames()}>
                <label>
                    Word:
                    <input type="text" value={this.state.value} onChange={this.handleChange} />
                </label>
                <input type="submit" value="Search" />
            </form>
            </div>
        );
      }
}


export default SearchForm;
