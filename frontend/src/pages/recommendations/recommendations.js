import React, { useState, useEffect } from 'react'
import { NavMenu } from '../menu/menu.js'
import { PULLER_HOST } from '../../constants.js'
import { recommendationsByMacd } from './components.js'

export function Recommendations () {
  const [byMacd, setByMacd] = useState([])

  useEffect(
    () => {
      fetch(`http://${PULLER_HOST}/recommendations/by_macd`)
        .then(response => response.json())
        .then((data) => {
          const { response } = data
          setByMacd(response)
        })
    }, [])

  return (<div className='flex'>
      {NavMenu()}
      <div className="grow h-14">
        <h2 className="text-5xl text-center">Recommendations</h2>
        {recommendationsByMacd(byMacd)}
      </div>
    </div>)
}
