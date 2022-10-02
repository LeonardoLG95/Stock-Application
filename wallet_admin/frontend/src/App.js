import React from 'react'
import { buyForm, sellForm, operationTable } from './Html'

function App () {
  const [symbolList, setSymbolList] = React.useState([])
  const [buyList, setBuyList] = React.useState([])
  const [sellList, setSellList] = React.useState([])

  React.useEffect(
    () => {
      fetch('http://127.0.0.1:8000/symbols')
        .then(response => response.json())
        .then((data) => {
          const { response } = data
          setSymbolList(response)
        })
    }, [])
  React.useEffect(
    () => {
      fetch('http://127.0.0.1:3000/buy_list')
        .then(response => response.json())
        .then((data) => {
          const { operations } = data
          setBuyList(operations)
        })
    }, [])
  React.useEffect(
    () => {
      fetch('http://127.0.0.1:3000/sell_list')
        .then(response => response.json())
        .then((data) => {
          const { operations } = data
          setSellList(operations)
        })
    }, [])

  return (
      <div>
        <div className="grid place-items-center h-screen">
          <h2 className="text-5xl">Wallet admin</h2>
          <div className="p-10 rounded grid space-y-5">
            <div className="py-3 px-5 bg-gray-50 text-center">Wallet evolution</div>
            <canvas className="p-10" id="chartLine"></canvas>
          </div>
          <div className='flex'>
          {buyForm(symbolList)}
          {sellForm(symbolList)}
          </div>
          <div className='flex'>
          {operationTable(buyList, 'green')}
          {operationTable(sellList, 'red')}
          </div>
        </div>
      </div>
  )
}

export default App
