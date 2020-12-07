import React, { useState } from 'react';
import './App.css';
import { Container, Grid } from 'semantic-ui-react'
import Nav from './components/Nav'
import HeaderRegion from './components/HeaderRegion'
import ResultsList from './components/ResultsList'
import SearchBox from './components/SearchBox'
import Footer from './components/Footer'

function App() {
  const [events, setEvents] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  let navStyle = {
    backgroundColor: '#77212E',
    position: 'fixed',
    height: 80,
    width: '100%',
    verticalAlign: 'middle',
    zIndex: 1
  }

  let footerStyle = {
    backgroundColor: '#77212E',
    height: 100,
    width: '100%',
    bottom: 0,
    verticalAlign: 'middle',
    zIndex: 100
  }

  return (
    <div className="App" style={{positive:"relative", minHeight:"100vh"}}>
      <Grid.Row style={navStyle}>
        <Nav/>
      </Grid.Row>

      <Container style={{paddingTop:100, marginBottom:150}}>
        <Grid centered padded style={{zindex:0}}>
          <Grid.Row>
            <HeaderRegion/>
          </Grid.Row>

          <Grid.Row>
            <SearchBox setEvents={setEvents} setIsLoading={setIsLoading}/>
          </Grid.Row>

          {/* TO-DO: change loading component */}
          <Grid.Row style={{paddingTop:50}}>
            {isLoading ? <p>Loading...</p> : <ResultsList events={events} />}
          </Grid.Row>
        </Grid>
      </Container>

      <Grid.Row style={footerStyle}>
        <Footer/>
      </Grid.Row>
    </div>
  );
}

export default App;
