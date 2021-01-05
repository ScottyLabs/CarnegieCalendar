import React from 'react'
import { Container } from 'semantic-ui-react'

export default function HeaderRegion () {
  let footerCSS = {
    fontSize: 16, 
    color: "#FFF5EE", 
    position: "relative", 
    paddingTop: 37, 
    textAlign: "center",
  }

  let attribCSS = {
    fontSize: 11
  }
  
  return (
    <Container text style={footerCSS}>
      Developed with <span role="img" aria-label="heart">❤️</span> by 
      <a href="https://scottylabs.org" target="_blank"> ScottyLabs</a>
      <br/>
      <span style={attribCSS}>
        Originally developed by
        <a href="https://andykong.org" target="_blank"> Andy Kong</a>
      </span>
    </Container>
  )
}