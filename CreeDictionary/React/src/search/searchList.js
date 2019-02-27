import React from 'react';

import './searchForm.css';

import { wordDetail, getData, getLoaded } from '../util';

import PropTypes from "prop-types";

class SearchList extends React.Component{
    /*static propTypes = {
        sended: PropTypes.boolean.isRequired,
        //this.props.sended
    };*/
    constructor(props) {
        super(props);

        this.state = {
            data: null,
            A: null,
        };
      }
    
      detail(item){
        alert(item);
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

    /*shouldComponentUpdate() {
        if ((!this.props.Words) || (this.props.Words !== this.state.data)) {
            return true;
        }
        return false;
      }*/

    render(props) {
        console.log('prop sended: ' + this.props.sended);
        console.log('Data sended: ' + JSON.stringify(this.props.Words));
        if (!this.props.Words) {
            console.log('prop sended: ' + this.props.sended);
            console.log('Data sended: ' + JSON.stringify(this.props.Words));
            return (<div><h1>Error page</h1></div>);
        }
        if (this.props.Words) {
            return (
                <div className="centre"> 
                <section>
                    <ul className="centreli">
                        {this.props.Words.map((wordlist) => {
                                return <li key={wordlist.id} onClick={() => this.detail(wordlist.context)}>{wordlist.context}</li>
                            })
                        }
                    </ul>
                </section>
                </div>
            );
        }
      }
}

export default SearchList;

/*
onClick = {() => {this.props.onClick(catName)}}
{this.state.Words.map((task, i) => <li key={i}>{task.context}</li>)}

constructor () {
    super()

    this.state {
      tasks: null
    }
  }

  componentDidMount () {
    fetch('/task')
      .then((data) => {
        return data.json()
      })
      .then((json) => {
        this.setState({ tasks: json.tasks })
      })
  }

  renderTaskList () {
    if (this.state.tasks) {
      return (
        <ul>
          {this.state.tasks.map((task, i) => <li key={i}>{task.name}</li>)}
        </ul>
      )
    }

    return <p>Loading tasks...</p>
  }
    render () {
        return (
            <div>
            <h1>Tasks</h1>
            {this.renderTaskList()}
            </div>
        );
    }
*/