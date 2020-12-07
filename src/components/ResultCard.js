import React from 'react'
import { Card, Icon } from 'semantic-ui-react'
import EventModal from './EventModal'

export default function ResultCard (props) {
  const [modalVisible, setModalVisible] = React.useState(false)

  const secsToMillis = 1000

  const dayFormatter = new Intl.DateTimeFormat('en-US', {'month': 'numeric', 'day': 'numeric', 'year': '2-digit'})
  const timeFormatter = new Intl.DateTimeFormat('en-US', {'hour': 'numeric', 'minute': 'numeric', 'hour12': true})

  const { description, summary, location, url } = props.event
  const startTimeRaw = new Date(props.event['start_time'] * secsToMillis)
  const endTimeRaw = new Date(props.event['end_time'] * secsToMillis)

  const startDay = dayFormatter.format(startTimeRaw)
  const endDay = dayFormatter.format(endTimeRaw)
  const startTime = timeFormatter.format(startTimeRaw)
  const endTime = timeFormatter.format(endTimeRaw)

  const dateRange = `${startDay} ${startTime} - ${startDay === endDay ? '' : endDay + ' '}${endTime}`

  const maxDescLength = 200
  const descStyle = { 'overflow': 'hidden', 'wordBreak': 'break-word', 'textOverflow': 'ellipsis'}
  const linkStyle = { 'overflow': 'hidden', 'whiteSpace': 'nowrap', 'textOverflow': 'ellipsis', 'paddingTop': 5}

  const cardClick = e => {
    if (!e.target.classList.contains('event-href')) {
      e.preventDefault()
      setModalVisible(!modalVisible)
    }
  }

  return (
    <Card style={{marginBottom: 50, backgroundColor: 'snow', height: 240, padding: 10}} href='#' onClick={cardClick}>
      <EventModal description={description}
                  summary={summary}
                  dateRange={dateRange}
                  url={url}
                  location={location}
                  open={modalVisible} />
      <Card.Content>
        <Card.Header>{summary}</Card.Header>
        <Card.Meta>
          <div className='date' style={{paddingTop:5}}>
            <Icon name="clock"/>{dateRange}
          </div>
          {location && <div className='location' style={{paddingTop:5}}>
            <Icon name="map marker"/>{location}
          </div>}
          {url && <div className='link' style={linkStyle}>
            <Icon name="paperclip"/>
            <a href={url} rel='noopener noreferrer' target='_blank' className='event-href'>{url}</a>
          </div>}
        </Card.Meta>
        <Card.Description>
          <p style={descStyle}>{description.length <= maxDescLength ? description
            : description.substring(0, maxDescLength) + '...'}</p>
        </Card.Description>
      </Card.Content>
    </Card>
  )
}