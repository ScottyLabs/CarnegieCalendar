import React from 'react'
import ResultCard from './ResultCard'
import { Card } from 'semantic-ui-react'

export default function ResultsList (props) {
  const getEventID = event => event.description
  let count = 0

  return (
    <Card.Group itemsPerRow={2} stackable style={{width: '80%'}}>
      {props.events.map(event => {
        event = <ResultCard event={event} key={count} />
        count += 1
        return event
      })}
    </Card.Group>
  )
}