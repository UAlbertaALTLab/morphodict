import React from 'react';

import './searchForm.css';

const url = '/api/form-submit-url';

class SearchForm extends React.Component{
    state = {
        sended: false,
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
        /*alert('A keyword was submitted: ' + this.state.value);*/
        event.preventDefault();
        const data = new FormData(event.target);
        this.setState({
            sended: true,
        })
        
        fetch(url,{
            method: 'POST',
            body: data,
        })
        .then(response =>{
            if (!response.ok) {
                alert('Connection error a word "' + this.state.value + '" was not submitted');
                console.log('connection error');
            }
            //response.json();
        })
        .catch(error => console.log('error') );
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
            <div className={this.getClassNames()}>
            <form onSubmit={this.handleSubmit.bind(this)}>
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
