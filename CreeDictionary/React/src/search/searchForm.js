/*
* SearchForm class
* 
*   Returns Searchform (user input area and submit button)
*   Fetch on SearchWords when click onSubmit(search)
*/

import React from 'react';

import { withRouter } from 'react-router-dom';

class SearchForm extends React.Component {

  constructor(props) {
    super(props);
    this.state = { value: '' };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  /* 
  * Used when user inputs word
  * Sets state value to user input
  */
  handleChange(event) {
    this.setState({
      value: event.target.value,
    });
  }

  handleChar(char) {
    this.setState({
      value: this.state.value + char,
    });
  }

  /*
  * Used when user submits the word (When search the word)
  * Fetch the user input 
  * Set response to state.Words
  */
  handleSubmit(event) {
    event.preventDefault();
    this.props.history.push('/search/' + this.state.value);
  }

  /*
  * Used to switch between style of searchform
  */
  getClassNames() {
    let classNames = 'search';
    if (this.state.Words) {
      classNames += 'isTrue';
    }
    return classNames;
  }

  //render
  render() {
    return (
      <div className="card-body">
        <form onSubmit={this.handleSubmit.bind(this)} className="form-group" id="Search" method='POST'>
          <div className="form-row">
            <label> Word:</label>
            <div className="col">
              <input type="text" value={this.state.value} onChange={this.handleChange} className="form-control" />
            </div>
            <div className="col">
              <button type="submit" className="btn btn-primary btn-sm">Search</button>
            </div>
          </div>
          <div className="form-row">
            <p className="btn btn-default btn-link" onClick={() => this.handleChar("â")}>â</p>
            <p className="btn btn-default btn-link" onClick={() => this.handleChar("ê")}>ê</p>
            <p className="btn btn-default btn-link" onClick={() => this.handleChar("î")}>î</p>
            <p className="btn btn-default btn-link" onClick={() => this.handleChar("ô")}>ô</p>
            <p className="btn btn-default btn-link" onClick={() => this.handleChar("ā")}>ā</p>
            <p className="btn btn-default btn-link" onClick={() => this.handleChar("ē")}>ē</p>
            <p className="btn btn-default btn-link" onClick={() => this.handleChar("ī")}>ī</p>
            <p className="btn btn-default btn-link" onClick={() => this.handleChar("ō")}>ō</p>
          </div>
        </form>
      </div>
    );
  }
}

export default withRouter(SearchForm);
