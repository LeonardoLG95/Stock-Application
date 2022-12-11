import React from 'react'
import tableSort from 'table-sort-js/table-sort.js'

export function recommendationsByMacd (data) {
  tableSort()

  function row (stock) {
    return (<tr className="bg-white-500 border-b transition duration-300 ease-in-out">
        <td className="font-light px-6 py-4 text-center">{stock.start}</td>
        <td className="font-light px-6 py-4 text-center">{stock.symbol}</td>
        <td className="font-light px-6 py-4 text-center">{stock.name}</td>
        <td className="font-light px-6 py-4 text-center">{stock.last_close}</td>
        <td className="font-light px-6 py-4 text-center">{stock.macd_signal < 0 ? stock.macd - (stock.macd_signal) : stock.macd - stock.macd_signal}</td>
        <td className="font-light px-6 py-4 text-center">{stock.industry}</td>
        </tr>
    )
  }

  return (<table className="table-auto p-10 table-sort">
  <thead className="bg-white-500 border-b">
    <tr>
      <th scope='col' className='font-medium px-6 py-4 text-center'>Start</th>
      <th scope='col' className='font-medium px-6 py-4 text-center'>Symbol</th>
      <th scope='col' className='font-medium px-6 py-4 text-center'>Name</th>
      <th scope='col' className='font-medium px-6 py-4 text-center'>Last close $</th>
      <th scope='col' className='font-medium px-6 py-4 text-center'>MACD difference</th>
      <th scope='col' className='font-medium px-6 py-4 text-center'>Industry</th>
    </tr>
  </thead>
  <tbody>
    {data ? data.map(stock => row(stock)) : <tr><td></td><td></td><td>Not able to load stocks by MACD...</td><td></td><td></td><td></td></tr>}
  </tbody>
  </table>)
}
