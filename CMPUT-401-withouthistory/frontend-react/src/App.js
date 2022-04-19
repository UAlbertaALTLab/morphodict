import "./App.css";
import "./components/style.css";

import Layout from "./components/Layout";
import { Route } from "react-router-dom";
import WordEntry from "./components/WordEntry";
import About from "./components/About";
import ContactUs from "./components/ContactUs";
import Welcome from "./components/Welcome";
import CreeDictionarySettings from "./components/CreeDictionarySettings";
import SearchResult from "./components/SearchResult";
import AbbreviationsLegend from "./components/AbbreviationsLegend";

//Needed to make calls to our fun api
import { QueryClient, QueryClientProvider } from "react-query";

function App() {
  const queryClient = new QueryClient();


  return (
    <div>
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
          <Route exact path="/cree-dictionary-settings">
            <CreeDictionarySettings></CreeDictionarySettings>
          </Route>
          <Route
            exact
            path="/word/*"
            render={(props) => <WordEntry {...props}></WordEntry>}
          ></Route>
          <Route path="/search/:id" exact component={SearchResult} />
          <Route exact path="/cree-dictionary-legend">
            <AbbreviationsLegend></AbbreviationsLegend>
          </Route>
        </Layout>
      </QueryClientProvider>
    </div>
  );
}

export default App;
