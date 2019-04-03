import React from 'react';

import i18next from '../../utils/translate';

class Definition extends React.Component {
    render(){
        return(
            <div className="col-12">
                        <section>
                            <h1>{this.props.word}</h1>
                        </section>
                        <div className="card">
                            <div className="card-header">
                                <h2 className="card-title">{i18next.t('Definition')}</h2>
                            </div>
                            <section className="card-body">
                                {this.props.definition.map((e) => {
                                    return (
                                        <h3 key={e.id} className="text-center" >{e.context}<br /><sub>{e.source}</sub></h3>)
                                })}
                            </section>
                        </div>
                    </div>
        );
    }
}

export default Definition;