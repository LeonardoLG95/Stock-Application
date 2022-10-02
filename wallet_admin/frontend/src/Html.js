import React from 'react'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'

export function buyForm (symbolList) {
  const submit = async (e) => {
    e.preventDefault()

    const form = new FormData(e.target)
    const data = Object.fromEntries(form.entries())

    console.log(data)
    await fetch('http://localhost:3000/record_buy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data
      })
    })
  }
  const button = <input className="bg-green-500 hover:bg-green-400 text-white font-bold py-2 px-4 border-b-4 border-green-700 hover:border-green-500 rounded" type="submit" value="Register Buy"></input>

  return operationForm(symbolList, button, submit)
}

export function sellForm (symbolList) {
  const submit = async (e) => {
    e.preventDefault()

    const form = new FormData(e.target)
    const data = Object.fromEntries(form.entries())

    await fetch('http://localhost:3000/record_sell', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data
      })
    })
  }
  const sellButton = <input className="bg-red-500 hover:bg-red-400 text-white font-bold py-2 px-4 border-b-4 border-red-700 hover:border-red-500 rounded" type="submit" value="Register Sell"></input>

  return operationForm(symbolList, sellButton, submit)
}

function operationForm (symbolList, submitButton, submitFunction) {
  const [operationDate, setOperationDate] = React.useState(new Date())

  return <form className='p-10 rounded grid space-y-5' onSubmit={submitFunction}>
            <select placeholder="Symbol" name="symbol">
              {symbolList ? symbolList.map(symbol => <option value={symbol} key={symbol}>{symbol}</option>) : <option value="null">Not able to load options...</option>}
            </select>
            <input placeholder="Stock price $" name='stockPrice' type="number"></input>
            <input placeholder="Quantity" name='quantity' type="number"></input>
            <input placeholder="Operation price $" name='usdPrice' type="number"></input>
            <input placeholder="Operation price €" name='eurPrice' type="number"></input>
            <DatePicker placeholderText='Date' name="operationDate" value={operationDate} selected={operationDate} onChange={(date) => setOperationDate(date)} />
            {submitButton}
        </form>
}

export function operationTable (operations, color) {
  const row = (_id, operationDate, symbol, quantity, eurPrice, color) => {
    const deleteButton = (_id) => {
      return <form>
        <input className="bg-red-500 hover:bg-red-400 py-2 px-4 border-b-4 border-red-700 hover:border-red-500 rounded" type="submit"></input>
        </form>
    }

    return <tr key={_id} className={`bg-white-500 border-b transition duration-300 ease-in-out hover:bg-${color}-100`}>
        <td className="font-light px-6 py-4 text-center">{operationDate}</td>
        <td className="font-light px-6 py-4 text-center">{symbol}</td>
        <td className="font-light px-6 py-4 text-center">{quantity}</td>
        <td className="font-light px-6 py-4 text-center">{eurPrice}€</td>
        <td className="font-light px-6 py-4 text-center">{deleteButton(_id)}</td>
      </tr>
  }

  return <div className='p-10'><table className="table-auto p-10 ">
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
    {operations ? operations.map(o => row(o._id, o.operationDate, o.symbol, o.quantity, o.eurPrice, color)) : <tr><td></td><td>Not able to load operations...</td><td></td></tr>}
    </tbody>
  </table></div>
}
