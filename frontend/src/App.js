import React, { useState, useEffect } from 'react'
import { chart, buyForm, sellForm, operationTable } from './Html'

function App () {
  const [symbolList, setSymbolList] = useState([])
  const [buyOperations, setBuyOperations] = useState(null)
  const [sellOperations, setSellOperations] = useState(null)

  // useEffect(
  //   () => {
  //     fetch('http://127.0.0.1:8000/symbol_prices', {
  //       method: 'POST',
  //       headers: { 'Content-Type': 'application/json' },
  //       body: JSON.stringify({ symbol: 'AAPL', resolution: 'M', start_date: 0, end_date: 0 })
  //     })
  //       .then(response => response.json())
  //       .then((data) => {
  //         const { response } = data
  //         chart(response)
  //       })
  //   }, [])
  useEffect(
    () => {
      fetch('http://127.0.0.1:8000/symbols')
        .then(response => response.json())
        .then((data) => {
          const { response } = data
          setSymbolList(response)
        })
    }, [])
  useEffect(
    () => {
      fetch('http://127.0.0.1:3010/buy_list')
        .then(response => response.json())
        .then((data) => {
          const { operations } = data
          setBuyOperations(operations)
        })
    }, [])
  useEffect(
    () => {
      fetch('http://127.0.0.1:3010/sell_list')
        .then(response => response.json())
        .then((data) => {
          const { operations } = data
          setSellOperations(operations)
        })
    }, [])
  useEffect(
    () => {
      if (buyOperations && sellOperations) {
        chart(buyOperations, sellOperations)
      }
    }, [buyOperations, sellOperations])

  return (
      <div>
        <div className="grid place-items-center h-screen">
          <h2 className="text-5xl">Wallet admin</h2>
          <div className="p-500 rounded grid space-y-5">
            <div className="py-300 px-500 bg-gray-50 text-center">Wallet evolution</div>
            <canvas className="p-10" id="chartLine"></canvas>
          </div>
          <div className='flex'>
          {buyForm(symbolList)}
          {sellForm(symbolList)}
          </div>
          <div className='flex'>
            <div className='p-10'>
              <table className="table-auto p-10 ">
                <thead className={'bg-white-500 border-b'}>
                  <tr>
                    <th scope='col' className='font-medium px-6 py-4 text-center'>Date</th>
                    <th scope='col' className='font-medium px-6 py-4 text-center'>Symbol</th>
                    <th scope='col' className='font-medium px-6 py-4 text-center'>Quantity</th>
                    <th scope='col' className='font-medium px-6 py-4 text-center'>Final price</th>
                    <th scope='col' className='font-medium px-6 py-4 text-center'></th>
                  </tr>
                </thead>
                <tbody>
                  {operationTable(buyOperations, 'buy')}
                </tbody>
              </table>
            </div>
            <div className='p-10'>
              <table className="table-auto p-10 ">
                <thead className={'bg-white-500 border-b'}>
                  <tr>
                    <th scope='col' className='font-medium px-6 py-4 text-center'>Date</th>
                    <th scope='col' className='font-medium px-6 py-4 text-center'>Symbol</th>
                    <th scope='col' className='font-medium px-6 py-4 text-center'>Quantity</th>
                    <th scope='col' className='font-medium px-6 py-4 text-center'>Final price</th>
                    <th scope='col' className='font-medium px-6 py-4 text-center'></th>
                  </tr>
                </thead>
                <tbody>
                  {operationTable(sellOperations, 'sell')}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
  )
}

export default App
