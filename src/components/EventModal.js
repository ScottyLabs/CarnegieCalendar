import React from 'react'
import { Button, Card, Header, Icon, Modal, Segment } from 'semantic-ui-react'

export default function EventModal (props) {
  const { description, summary, location, url, dateRange } = props
  const descStyle = { wordWrap: 'break-word', whiteSpace: 'pre-wrap' }

  return (
    <Modal
      closeIcon
      dimmer='inverted'
      open={props.open}
      style={{width: '80%', height: '80%', overflow: 'scroll', textOverflow: 'ellipsis', background: 'snow'}}
    >
      <Modal.Header style={{background:'#77212E', color:'snow'}}>Event Details</Modal.Header>
      <Modal.Content style={{background:'snow'}}>
        <Modal.Description>
          <Segment>
            <Header>{summary}</Header>
            <div className='date'><Icon name="clock"/>{dateRange}</div>
            {location && <div className='location'><Icon name="map marker"/>{location}</div>}
            {url && <div className='link'>
              <Icon name="paperclip"/>
              <a href={url} rel='noopener noreferrer' target='_blank'>{url}</a>
            </div>}
          </Segment>
          <p style={descStyle}>
            {description}
          </p>
        </Modal.Description>
      </Modal.Content>
    </Modal>
  )
}