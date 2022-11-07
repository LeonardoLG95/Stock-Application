import React from 'react'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'
import Chart from 'chart.js/auto'
import { PULLER_HOST, WALLET_ADMIN_HOST } from './constants.js'

export function refreshingData () {
  return <div>
    <p>Loading data already...</p>
    <img src='/loading.gif'></img>
    </div>
}
export function refreshDataButton () {
  const submit = async (e) => {
    e.preventDefault()
    await fetch(`http://${PULLER_HOST}/load_data`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    window.location.reload()
  }

  return <form className='p-10 rounded grid space-y-5' onSubmit={submit}>
    <input className="bg-red-500 hover:bg-red-400 text-white font-bold py-2 px-4 border-b-4 border-red-700 hover:border-red-500 rounded" type="submit" value="Refresh data"></input>
  </form>
}
export async function chart (buyOperations, sellOperations) {
  const chartData = await fetch(`http://${WALLET_ADMIN_HOST}/wallet_evolution`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ buyOperations, sellOperations, resolution: 'M' })
  })
    .then(response => response.json())
    .then(data => data.result)

  console.log(chartData)
  const time = []
  chartData.forEach(e => time.push(e[0]))

  const price = []
  chartData.forEach(e => price.push(e[1]))

  const config = {
    type: 'line',
    data: {
      labels: time,
      datasets: [{
        label: 'Wallet $',
        data: price,
        borderColor: 'rgba(0, 0, 0, 1)',
        borderWidth: 1
      }],
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    }
  }
  const canvas = document.getElementById('chartLine').getContext('2d')
  window.priceLine = new Chart(canvas, config)
}

export function buyForm (symbolList) {
  const submit = async (e) => {
    e.preventDefault()
    const form = new FormData(e.target)
    const data = Object.fromEntries(form.entries())

    await fetch(`http://${WALLET_ADMIN_HOST}/record_buy`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data
      })
    })
    window.location.reload()
  }
  const button = <input className="bg-green-500 hover:bg-green-400 text-white font-bold py-2 px-4 border-b-4 border-green-700 hover:border-green-500 rounded" type="submit" value="Register Buy"></input>

  return operationForm(symbolList, button, submit)
}

export function sellForm (symbolList) {
  const submit = async (e) => {
    e.preventDefault()
    const form = new FormData(e.target)
    const data = Object.fromEntries(form.entries())

    await fetch(`http://${WALLET_ADMIN_HOST}/record_sell`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data
      })
    })
    window.location.reload()
  }
  const sellButton = <input className="bg-red-500 hover:bg-red-400 text-white font-bold py-2 px-4 border-b-4 border-red-700 hover:border-red-500 rounded" type="submit" value="Register Sell"></input>

  return operationForm(symbolList, sellButton, submit)
}

function operationForm (stockList, submitButton, submitFunction) {
  const [operationDate, setOperationDate] = React.useState(new Date())

  return <form className='p-10 rounded grid space-y-5' onSubmit={submitFunction}>
            <DatePicker placeholderText='Date' name="operationDate" value={operationDate} selected={operationDate} onChange={(date) => setOperationDate(date)} />
            <select placeholder="Symbol" name="symbol">
              {stockList ? stockList.map(stock => <option value={stock[1]} key={stock[1]}>{stock[0]}</option>) : <option value="null">Not able to load options...</option>}
            </select>
            <input placeholder="Quantity" name='quantity' type="number"></input>
            <input placeholder="Stock price $" name='stockPrice' type="number" step="0.01"></input>
            <input placeholder="Operation price €" name='eurPrice' type="number" step="0.01"></input>
            {submitButton}
        </form>
}

export function operationTable (operations, operationType) {
  const row = (operation, operationType) => {
    const deleteButton = (_id, operationType) => {
      const deleteAction = async (e) => {
        e.preventDefault()
        const form = new FormData(e.target)
        const data = Object.fromEntries(form.entries())

        console.log(data)
        await fetch(`http://${WALLET_ADMIN_HOST}/delete_${data.operationType}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            data
          })
        })
        window.location.reload()
      }

      return <form onSubmit={deleteAction}>
        <input className="bg-red-500 hover:bg-red-400 py-2 px-4 border-b-4 border-red-700 hover:border-red-500 rounded" type="image" src="/trashBin.svg"></input>
        <input type="hidden" name="_id" value={operation._id}></input>
        <input type="hidden" name="operationType" value={operationType}></input>
        </form>
    }

    const date = new Date(operation.operationDate)
    const pad = (s) => { return (s < 10) ? '0' + s : s }

    return <tr key={operation._id} className={'bg-white-500 border-b transition duration-300 ease-in-out'}>
        <td className="font-light px-6 py-4 text-center">{[pad(date.getDate()), pad(date.getMonth() + 1), date.getFullYear()].join('-')}</td>
        <td className="font-light px-6 py-4 text-center">{operation.symbol}</td>
        <td className="font-light px-6 py-4 text-center">{operation.quantity}</td>
        <td className="font-light px-6 py-4 text-center">{operation.stockPrice}$</td>
        <td className="font-light px-6 py-4 text-center">{operation.quantity * operation.stockPrice}$</td>
        <td className="font-light px-6 py-4 text-center">{operation.eurPrice}€</td>
        <td className="font-light px-6 py-4 text-center">{deleteButton(operation._id, operationType)}</td>
      </tr>
  }

  return operations ? operations.map(operation => row(operation, operationType)) : <tr><td></td><td>Not able to load operations...</td><td></td></tr>
}
