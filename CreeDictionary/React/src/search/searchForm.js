import React from 'react';

import './searchForm.css';
import SearchList from './searchList';

import { searchWord, getLoaded, getData } from '../util';

class SearchForm extends React.Component{
    state = {
        sended: false,
        Words: null,
    };
    constructor(props) {
        super(props);
        this.state = {value: ''};
        
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
      }
    
      handleChange(event) {
        this.setState({value: event.target.value});
      }

      handleSubmit(event) {
        event.preventDefault();
        //const data = new FormData(event.target);
        searchWord(this.state.value).then(response => {
          console.log(response)
          response.json().then(data => {
          console.log(JSON.stringify(data))
          this.setState({
            sended: true,
            Words: data.words,
          }, () => console.log(this.state))
        })
      });
        /*if (getLoaded() === false) {
          alert('Word not sent');
          console.log('SearchWord not sended: ' + getLoaded());
        }*/
      }

      getClassNames() {
        let classNames = 'search';
        if (this.state.sended === true) {
          classNames += 'isTrue';
        }
        return classNames;
      }

    render() {
        console.log('A '+JSON.stringify(this.state.Words))
        console.log('B '+this.state.Words)
        return (
          <div>
          <div>
          <form onSubmit={this.handleSubmit.bind(this)} className={this.getClassNames()}>
              <label>
                  Word:
                  <input type="text" value={this.state.value} onChange={this.handleChange} />
              </label>
              <input type="submit" value="Search" />
          </form>
          </div>
          <SearchList
              Words={this.state.Words}
              sended={this.state.sended}>
          </SearchList>
          </div>
        );
    }
}

export default SearchForm;
/*<SearchList>
              Word={this.state.Words}
              sended={this.state.sended}
            </SearchList> */
