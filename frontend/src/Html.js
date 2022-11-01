import React from 'react'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'
import Chart from 'chart.js/auto'

export async function chart (buyOperations, sellOperations) {
  const chartData = await fetch('http://127.0.0.1:3010/wallet_evolution', {
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

    await fetch('http://127.0.0.1:3010/record_buy', {
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

    await fetch('http://127.0.0.1:3010/record_sell', {
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
  const row = (_id, operationDate, symbol, quantity, eurPrice, operationType) => {
    const deleteButton = (_id, operationType) => {
      const deleteAction = async (e) => {
        e.preventDefault()
        const form = new FormData(e.target)
        const data = Object.fromEntries(form.entries())

        console.log(data)
        await fetch(`http://127.0.0.1:3010/delete_${data.operationType}`, {
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
        <input type="hidden" name="_id" value={_id}></input>
        <input type="hidden" name="operationType" value={operationType}></input>
        </form>
    }

    return <tr key={_id} className={'bg-white-500 border-b transition duration-300 ease-in-out'}>
        <td className="font-light px-6 py-4 text-center">{operationDate}</td>
        <td className="font-light px-6 py-4 text-center">{symbol}</td>
        <td className="font-light px-6 py-4 text-center">{quantity}</td>
        <td className="font-light px-6 py-4 text-center">{eurPrice}€</td>
        <td className="font-light px-6 py-4 text-center">{deleteButton(_id, operationType)}</td>
      </tr>
  }

  return operations ? operations.map(o => row(o._id, o.operationDate, o.symbol, o.quantity, o.eurPrice, operationType)) : <tr><td></td><td>Not able to load operations...</td><td></td></tr>
}
