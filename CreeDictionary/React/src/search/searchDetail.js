import React from 'react';

import './searchForm.css';

class SearchDetail extends React.Component{
    /*static propTypes = {
        sended: PropTypes.boolean.isRequired,
        //this.props.sended
    };*/
    constructor(props) {
        super(props);

        this.state = {
            det: null,
            A: null,
            word: null,
        };
      }

    /*shouldComponentUpdate() {
        if (this.props.sended === true && !this.props.Words) {
            return true;
        }
        return false;
      }*/

    render(props) {
        console.log('Detail: ' + JSON.stringify(this.props.det));
        if (!this.props.det) {
            return (
                <div className="centre"> 
                    <section>
                        <h1>{this.props.word}</h1>
                    </section>
                </div>
            );
        }
        return (
            <div className="centre"> 
                <div>
                    <h1>{this.props.word}</h1>
                </div>
                <section>
                    <ul className="centreli">
                        {this.props.det.map((wordlist) => {
                                return <li key={wordlist.id}>{wordlist.context}</li>
                            })
                        }
                    </ul>
                </section>
            </div>
        );
      }
}

export default SearchDetail;

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


/*if (this.props.Words && loaded && !this.state.detail) {
            console.log('Detail: ' + JSON.stringify(this.state.det));
            return (
                <div className="centre"> 
                <section>
                    <h1>{this.state.word}</h1>
                </section>
                </div>
            );
        }*/