import React from 'react'
import { Loader } from 'semantic-ui-react'

export default function Loading () {
  return (
    <Loader active inline='centered' size='large'
     style={{color: '#77212E', fontWeight: 'bold'}}>
      Loading
    </Loader>
  )
}