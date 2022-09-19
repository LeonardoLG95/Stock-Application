import React from 'react'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'

export function buyForm (symbolList) {
  const submit = async (e) => {
    e.preventDefault()

    const form = new FormData(e.target)
    const data = Object.fromEntries(form.entries())
    console.log(data)
  }

  const button = <input className="bg-green-500 hover:bg-green-400 text-white font-bold py-2 px-4 border-b-4 border-green-700 hover:border-green-500 rounded" type="submit" value="Register Buy"></input>

  return operationForm(symbolList, button, submit)
}

export function sellForm (symbolList) {
  const submit = async (e) => {
    e.preventDefault()
  }
  const sellButton = <input className="bg-red-500 hover:bg-red-400 text-white font-bold py-2 px-4 border-b-4 border-red-700 hover:border-red-500 rounded" type="submit" value="Register Sell"></input>

  return operationForm(symbolList, sellButton, submit)
}

function operationForm (symbolList, button, submitFunction) {
  const [operationDate, setOperationDate] = React.useState(new Date())

  return <form className='p-10 rounded shadow-lg grid space-y-5' onSubmit={submitFunction}>
            <select placeholder="Symbol" name="symbol">
              {symbolList ? symbolList.map(symbol => <option value={symbol} key={symbol}>{symbol}</option>) : <option value="null">Not able to load options...</option>}
            </select>
            <input placeholder="Stock price $" name='stock_price' type="number"></input>
            <input placeholder="Quantity" name='quantity' type="number"></input>
            <input placeholder="Operation price $" name='usd_price' type="number"></input>
            <input placeholder="Operation price €" name='eur_price' type="number"></input>
            <DatePicker placeholderText='Date' name="operationDate" value={operationDate} selected={operationDate} onChange={(date) => setOperationDate(date)} />
            {button}
        </form>
}
