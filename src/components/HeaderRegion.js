import React from 'react'
import { Container, Header } from 'semantic-ui-react'

export default function HeaderRegion (props) {
  const titleCSS = {
    fontSize: 60,
    marginTop: '0.5em',
    marginBottom: '0',
    color: "#77212E",
  }
  const subtitleCSS = {
    color: "#77212E"
  }
  return (
    <Container text style={{paddingBottom: "5%"}}>
      <Header as="h1" size="huge" style={titleCSS}>Carnegie Calendar</Header>
      <Header as='h3' style={subtitleCSS}>
        Your one-stop shop for everything happening at CMU.
      </Header>
    </Container>
  )
}