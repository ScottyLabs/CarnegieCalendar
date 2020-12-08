import React from 'react'
import { Header, Icon, Modal, Segment } from 'semantic-ui-react'

export default function EventModal (props) {
  const { description, summary, location, url, dateRange } = props

  const descStyle = { 
    overflowWrap: 'break-word', 
    wordBreak: 'break-all', 
    whiteSpace: 'pre-wrap' 
  }

  const modalStyle = {
    width: '80%', 
    height: '80%', 
    overflow: 'scroll', 
    textOverflow: 'ellipsis', 
    background: 'snow'
  }

  return (
    <Modal
      closeIcon
      closeOnDimmerClick={true}
      dimmer='inverted'
      open={props.open}
      style={modalStyle}
    >
      <Modal.Header style={{background:'#77212E', color:'snow'}}>
        Event Details
      </Modal.Header>
      <Modal.Content style={{background:'snow'}}>
        <Modal.Description>
          <Segment>
            <Header>{summary}</Header>
            <div className='date'><Icon name="clock"/>
              {dateRange}
            </div>
            {location && <div className='location'><Icon name="map marker"/>
              {location}
            </div> }
            {url && <div className='link'>
              <Icon name="paperclip"/>
              <a className='event-href' href={url} rel='noopener noreferrer' 
               target='_blank'>
                 Open Link
              </a>
            </div> }
          </Segment>
          <p style={descStyle}>
            {description}
          </p>
        </Modal.Description>
      </Modal.Content>
    </Modal>
  )
}