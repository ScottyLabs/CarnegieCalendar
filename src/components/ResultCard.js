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

  const cardStyle = {
    marginBottom: 50, 
    backgroundColor: 'snow', 
    height: 260, 
    padding: 10,
  }

  const headStyle = { 
    lineHeight: '1.5em', 
    maxHeight: '4.5em', 
    overflow: 'hidden', 
    whiteSpace: 'normal', 
    textOverflow: 'ellipsis'
  }

  const descStyle = { 
    lineHeight: '1.5em', 
    height: '4.5em', 
    overflow: 'hidden', 
    textOverflow: 'ellipsis',
  }

  const linkStyle = { 
    overflow: 'hidden', 
    whiteSpace: 'nowrap', 
    textOverflow: 'ellipsis', 
    paddingTop: 5}

  const cardClick = e => {
    if (!e.target.classList.contains('event-href')) {
      e.preventDefault()
      setModalVisible(!modalVisible)
    }
  }

  return (
    <Card style={cardStyle} href='#' onClick={cardClick}>
      <EventModal description={description}
                  summary={summary}
                  dateRange={dateRange}
                  url={url}
                  location={location}
                  open={modalVisible} />
      <Card.Content>
        <Card.Header style={headStyle}>
          {summary}
        </Card.Header>
        <Card.Meta>
          <div className='date' style={linkStyle}>
            <Icon name="clock"/>{dateRange}
          </div>
          {location && <div className='location' style={linkStyle}>
            <Icon name="map marker"/>{location}
          </div> }
          {url && <div className='link' style={linkStyle}>
            <Icon name="paperclip"/>
            <a href={url} rel='noopener noreferrer' target='_blank' 
             className='event-href'>
               {url}
            </a>
          </div> }
        </Card.Meta>
        <Card.Description style={descStyle}>
          {description}
        </Card.Description>
      </Card.Content>
    </Card>
  )
}