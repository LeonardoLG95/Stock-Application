import React from 'react'
import { buyForm, sellForm } from './Html'

function App () {
  const [symbolList, setSymbolList] = React.useState([])

  React.useEffect(
    () => {
      fetch('http://127.0.0.1:8000/symbols')
        .then(response => response.json())
        .then((data) => {
          const { response } = data
          setSymbolList(response)
        })
    }, [])

  // const resp = await fetch('http://127.0.0.1:8000/symbols')
  // const { response } = await resp.json()
  return (
      <div>
        <div className="grid place-items-center h-screen">
          <h2 className="text-5xl">Wallet admin</h2>
          <div className="shadow-lg rounded-lg overflow-hidden">
            <div className="py-3 px-5 bg-gray-50 text-center">Wallet evolution</div>
            <canvas className="p-10" id="chartLine"></canvas>
          </div>
          <div className='flex'>
          {buyForm(symbolList)}
          {sellForm(symbolList)}
          </div>
        </div>
      </div>
  )
}

export default App
