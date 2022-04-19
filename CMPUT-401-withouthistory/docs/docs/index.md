# Project Requirements

itwêwina paradigm layouts (ALT Lab)

<br />

## Executive Summary

_tânisi!_ (hello, how are you)

_itwêwina_ is a Plains Cree Dictionary that can deal with the rich word structure of Cree (and other Indigenous languages) to provide the community with resources. The problem is that the current project is not completely modular and it's tough to extract parts of it to be reused in other projects. Moreover, the front-end part of the project leaves much to be desired.

Our goal is to refactor the system to make it modular and easy to replicate in other sources. As an extension of this goal, we want to export a part of the system that is responsible for generating paradigm layout panes to be displayed and publish it as a separate package to PyPi. Moreover, we want to enhance the front-end by adding Reach JavaScript library to take advantage of components, extensibility and other features, and to reorganize the table display of paradigm layout panes to be more organized and fit for different screens sizes.

<br />

## Project Glossary

- **Derivational Paradigm**: The collection of all possible derived forms belonging to a lemma.
- **Derived Form**: A new wordform created from a lemma; this new wordform has a separate lemma with its own inflectional paradigm.
- **Inflection**: In linguistic morphology, inflection is a process of word formation in which a word is modified to express different grammatical categories such as tense, case, person, number, gender, and other.The inflection of verbs is called conjugation.
- **Inflectional Paradigm**: The collection of inflected wordforms belonging to a lemma. Informally known as the conjugations.
- **Lemma**: The base form of a word form; this is a form chosen to depict the basic representation of the paradigm. Unlike a stem or root, a lemma is always a valid word form.
- **Paradigm Layout**: A formal specification that describes how to arrange related wordforms (inflections or derived wordforms) in a table.
- **User Query** (also query, search string): How the user writes their search intent, as a series of Unicode code points. This might be a messy, misspelled, strangely written string.
- **Wordform**: In linguistics, the different ways that a word can exist in a language. A wordform must be able to exist by itself.

> [**Parent Project Glossary**](https://github.com/UAlbertaALTLab/morphodict/blob/main/docs/glossary.md)

<br />

## User Stories

### US 1.01 - Existing Pages use React

> **As a** developer, **I want to** update the existing front end with React, **so that** I can benefit from replicating components, performance enhancement, and JavaScript library.
>
> **Acceptance Test:**
>
> 1. New React website has the same set of pages and content as the existing one.

### US 1.02 - Settings and Search use React

> **As a** developer, **I want to** update the settings and search features with React, **so that** they are easy to replicate and in agreement with the rest of the project.
>
> **Acceptance Test:**
>
> 1. Able to use display options (paradigm labels, emoji for nouns, etc) with updated React page.
> 2. Able to output the same result from a user query, as the existing system.

### US 1.03 - Paradigm Panes Display with React

> **As a** developer, **I want to** update the displaying of paradigm panes with the use of React, **so that** rows with wordforms are easily replicable and modular enough to be partially displayed.
>
> **Acceptance Test:**
>
> 1. .paradigm\_\_table table is updated with React components.
> 2. .HACK-overflow-x-scroll class is not needed to display panes correctly.
> 3. Panes contain appropriate labels (1st,2nd) and display type configured in options (English, linguistic)

### US 1.04 - Scalable Page Size

> **As a** user, **I want** the displayed page to fill most of the screen I am using, **so that** I can see more information at once and don't have to scroll for long.
>
> **Acceptance Test:**
>
> 1. Mobile page view displays the majority of content inside the screen in 100% zoom and scrolls if needed.
> 2. Page style takes advantage of large screen size to fit information in multiple columns.

### US 1.05 - Distinguish Found-In-Literature words

> **As a** user, **I want** distinguish between the words found in literature, **so that** I can make more educated decisions about the words I am using.
>
> **Acceptance Test:**
>
> 1. Style for Found-In-Literature words is noticeably different.
> 2. System provides a legend to how Found-In-Literature words are defined.

### US 1.06 - Collapsible Cards for Tense Inflections

> **As a** user, **I want** open and collapse tense inflections for a pane, **so that** I can make a better use of my screen size and can compare different forms.
>
> **Acceptance Test:**
>
> 1. Inflections for paradigm open and close in dropdown fashion.

### US 1.07 - Pane Element Specific Labels

> **As a** user, **I want** see paradigm labels when I hover over a wordform, **so that** the information is communicated more clear.
>
> **Acceptance Test:**
>
> 1. Tooltip with proper label appears when hovered over a wordform

### US 1.08 - Speaker Options

> **As a** user, **I want** to see different speaker options when I play audio, **so that** I am able to hear different pronunciations.
>
> **Acceptance Test:**
>
> 1. Speaker options are displayed.
> 2. Speaker options are not duplicated (to infinity) as it is right now.

### US 1.09 - Pane Element Specific Audio

> **As a** user, **I want** to an audio of a wordform inside of a pane, **so that** I can hear how it is pronounced.
>
> **Acceptance Test:**
>
> 1. Speaker options are displayed.
> 2. Speaker options are not duplicated (to infinity) as it is right now.

### US 1.10 - Tooltips Copying

> **As a** user, **I want** to copy from existing tooltips, **so that** I can be more efficient.
>
> **Acceptance Test:**
>
> 1. Able to copy from tooltips.

### US 2.01 - REST API URI

> **As a** developer, **I want** my back end to provide correct REST urls, **so that** the project adhers to standards and is easier to understand as a result.
>
> **Acceptance Test:**
>
> 1. API uri provided are following [REST uri rules](https://blog.restcase.com/7-rules-for-rest-api-uri-design/).

### US 2.02 - JSON Responses

> **As a** developer, **I want** my back end to return data encoded as a JSON, **so that** the data is easier to parse.
>
> **Acceptance Test:**
>
> 1. API returns data as JSON.

### US 2.03 - Modular Responses

> **As a** developer, **I want** returned data to be modular, **so that** it can be partially displayed by the front end.
>
> **Acceptance Test:**
>
> 1. Data is structured as a dictionary with key and values rather than as a string.

### US 3.01 - Panes.py Work Independently

> **As a** developer, **I want** to extract panes.py file to a different repository, **so that** I can replicate it elsewhere.
>
> **Acceptance Test:**
>
> 1. Extracted panes.py generates paradigm for a given lemma (input).
> 2. Extracted panes.py is able to work independently of other project.

### US 3.02 - Panes.py Published to PyPi

> **As a** developer, **I want** extracted panes.py to be published as a package on PyPi, **so that** I can quickly install it in a different project.
>
> **Acceptance Test:**
>
> 1. pip install extracted package allows generating panes layout.

### US 3.03 - Package is Reused inside the Project

> **As a** developer, **I want** reuse packaged version of panes.py, **so that** I have greater code modularity and code independence.
>
> **Acceptance Test:**
>
> 1. Refactored system produces proper layout with the use of installed package.

### US 4.01 - REST API Testing

> **As a** developer, **I want** to have tests of updated REST API, **so that** I can check the API is working as planned.
>
> **Acceptance Test:**
>
> 1. API URI related to paradigm generation are well tested.

### US 4.02 - Integration Testing

> **As a** developer, **I want** reuse existing integration tests, **so that** I know the whole system is stable and working.
>
> **Acceptance Test:**
>
> 1. Integration tests of the system are running successfully.

### US 4.03 - CI/CD

> **As a** developer, **I want** to have a running CI/CD system on GitHub, **so that** quickly check system status and deploy latest stable version.
>
> **Acceptance Test:**
>
> 1. CI runs a set of tests when the system is pushed to GitHub.
> 2. CD deploys the project on merge to master/release.

### US 5.01 - Cybera Instance

> **As a** developer, **I want** to have a Cybera instance, **so that** I can imitate production environment.
>
> **Acceptance Test:**
>
> 1. Cybera instance is stable and running.

### US 5.02 - Project Deployed

> **As a** developer, **I want** to deploy the project on Cybera instance, **so that** I can access it from anywhere and to test in prod env.
>
> **Acceptance Test:**
>
> 1. Project is available at port 80 of the Cybera instance.

### US 6.01 - Customizable Dictionary

> **As a** developer **I want to** reuse morphodict setup with other languages, **so that** other developers in the field can benefit from this open project.
>
> **Acceptance Test:**
>
> 1.  Local server runs with dictionary of other language.

<br />

## MoSCoW of Prioritization

> ### Must Have

> - US 1.01 - Existing Pages use React
> - US 1.02 - Settings and Search use React
> - US 1.03 - Paradigm Panes Display with React
> - US 1.04 - Scalable Page Size
> - US 1.06 - Collapsible Cards for Tense Inflections
> - US 2.01 - REST API URI
> - US 2.02 - JSON Responses
> - US 2.03 - Modular Responses
> - US 3.01 - Panes.py Work Independently
> - US 3.02 - Panes.py Published to PyPi
> - US 3.03 - Package Reused inside the Project
> - US 4.02 - Integration Testing
> - US 5.01 - Cybera Instance
> - US 5.02 - Project Deployed

> ### Should Have

> - US 1.05 - Distinguish Found-In-Literature words
> - US 4.01 - REST API Testing
> - US 4.03 - CI/CD

> ### Could Have

> - US 1.07 - Pane Element Specific Labels
> - US 1.08 - Speaker Options
> - US 1.10 - Tooltips Copying

> ### Would Like But Won't Get

> - US 1.09 - Pane Element Specific Audio
> - US 6.01 - Customizable Dictionary

<br />

## Similar Products

### [Wikipedia](https://en.wikipedia.org/wiki/Main_Page)

> In particular their language sections.

> #### Why:

> Seems odd but Wikipedia does have a list of every language and how they work.

> #### Features:

> Can search and find where a word comes from and their base form.

> #### Inspiration (design):

> For this project, not much can be taken outside of the general design.  
> Design that we could use is the clean layout of the search queries.

> #### Inspiration (code):

> Code wise we can't use anything from Wikipedia as our project has a backend with a design already in the mind of the client.

### [Dictionary.com](https://www.dictionary.com/browse/global)

> #### Why:

> Gives a nice and clean overview something similar to a paradigm.  
> While it only works for English it does do a similar job as us.

> #### Features:

> Gives relatively clean bit of information for one word and how it related to over words.

> #### Inspiration (design):

> Helps us to see how we might use the screen space in something more professional.  
> The way they make their pages reactive to the current screen size is both helpful and needed by our client.

> #### Inspiration (code):

> Since it is closed source we can't really use code as an inspiration.

### [Google Translate](https://translate.google.ca/)

> #### Why:

> The design of their search results.

> #### Features:

> Information being compressed into a small screen supplying more information when the user asks for it.

> #### Inspiration (design):

> Google packs a lot of information in a very small window and still makes it useful.  
> In fact, their translated words card is almost like a paradigm. So, we can use it as an inspiration for how to deal with a lot of information for each "word".

> #### Inspiration (code):

> Closed source so we can't really take anything from the current project.

### [Thesaurus.plus](https://thesaurus.plus/related/paradigm/template)

> #### Why:

> The way it displays information to screen prevents information overload.

> #### Features:

> The way models are shown to the user.

> #### Inspiration (design):

> We can use their design to help us learn how to display information to the user.

> #### Inspiration (code):

> Closed source so we can't really take anything from the current project.

### [dictionary.blackfoot.atlas-ling](https://dictionary.blackfoot.atlas-ling.ca)

> #### Why:

> Similar goal to what we want to carry out.

> #### Features:

> Gives us the correct information for us. In fact, all we're trying to do is setup an expansion to this website more or less.

> #### Inspiration (design):

> We can use their design to help us learn how to display information to the user.

> #### Inspiration (code):

> Closed source so we can't really take anything from the current project

<br />

## Open-Source Projects:

### [Crate](https://github.com/atulmy/crate)

> A sample web and mobile application built with Node, Express, React, React Native, Redux and GraphQL.
>
> 1. UI design seems original and could serve as an example into using React and building the front end.
> 2. Screen sizes look different which implies it scales differently according to screen size, which is another task of our project.
> 3. API in the project could also appear helpful to make it more React friendly.

### [React Kanban](https://github.com/markusenglund/react-kanban)

> Another React website.
>
> 1. Has a lot of interactive components may be helpful implementing paradigm panes.
> 2. Might prove helpful in project planning/tracking.

### [Hacker News Clone Remix/React](https://github.com/clintonwoo/hackernews-remix-react)

> More basic example of React website that has common structuring with current implementation of the project.
>
> 1. Pagination.
> 2. Support/About and other small pages.
> 3. Pretty raw formatting that could inspire reworked pane implementation.

<br />

## Technical Resources

### [Boostrap V5](https://getbootstrap.com/)

> We want to use it so that our front-end is:
>
> 1. Pages can be reactive to the screen we give them.
> 2. We can add cards to make changes for particular components.
> 3. We can colors nicely and make the pages modular.

### [PopperJs](https://popper.js.org/)

> We can make pop pages for the current words and we can hide aspects of the page to make it both clean and preserve screen space.
>
> 1. We can pop aspects of the current word for the user instead of just displaying it.
> 2. Can make sounds page appear on the word and not take up unneeded screen pages.

### [Pip-Tools](https://github.com/jazzband/pip-tools)

> Gives us the ability to control pip packages and all the information related to the current package.

### [Poetry](https://python-poetry.org/)

> Poetry helps tp quickly package and publish a project to PyPi.

### [ReactJS](https://reactjs.org/)

> We can use react to better keep track of everything all in one application instead of keeping things as components.

### [Django](https://www.djangoproject.com/)

> The original project is built in Django framework that allows separating of the projects parts into sections.

### [Python](https://www.python.org/)

> Django is run on Python programming language.
