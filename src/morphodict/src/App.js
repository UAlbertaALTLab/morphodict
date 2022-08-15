import "./App.css";
import "./components/style.css";

import Layout from "./components/Layout";
import {Route} from "react-router-dom";
import {Helmet} from 'react-helmet'
import WordEntry from "./components/WordEntry";
import About from "./components/About";
import ContactUs from "./components/ContactUs";
import Welcome from "./components/Welcome";
import Settings from "./components/Settings";
import SearchResult from "./components/SearchResult";
import AbbreviationsLegend from "./components/AbbreviationsLegend";

//Needed to make calls to our fun api
import {QueryClient, QueryClientProvider} from "react-query";

function App() {
    const queryClient = new QueryClient();

    return (
        <div>
            <Helmet>
                <meta charSet="utf-8"/>
                <title>{process.env.REACT_APP_NAME}</title>
            </Helmet>
            <QueryClientProvider client={queryClient}>
                <Layout>
                    <Route exact path="/">
                        <Welcome></Welcome>
                    </Route>
                    <Route exact path="/about">
                        <About></About>
                    </Route>
                    <Route exact path="/contact-us">
                        <ContactUs></ContactUs>
                    </Route>
                    <Route exact path="/settings">
                        <Settings></Settings>
                    </Route>
                    <Route
                        exact path="/word/*" component={WordEntry}/>
                    <Route path="/search/:id" exact component={SearchResult}/>
                    <Route exact path="/cree-dictionary-legend">
                        <AbbreviationsLegend></AbbreviationsLegend>
                    </Route>
                </Layout>
            </QueryClientProvider>
        </div>
    );
}

export default App;
