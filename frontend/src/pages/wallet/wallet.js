import React, { useState, useEffect } from 'react'
import { priceChart, pieChart, buyForm, sellForm, operationTable, refreshDataButton, refreshingData } from './components.js'
import { PULLER_HOST, WALLET_ADMIN_HOST } from '../../constants.js'
import { NavMenu } from '../menu/menu.js'

export function WalletEvolution () {
  const [symbolList, setSymbolList] = useState([])
  const [buyOperations, setBuyOperations] = useState(null)
  const [sellOperations, setSellOperations] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(
    () => {
      fetch(`http://${PULLER_HOST}/is_running`)
        .then(response => response.json())
        .then((data) => {
          const { response } = data
          setIsLoading(response)
        })
    }, [])
  useEffect(
    () => {
      fetch(`http://${PULLER_HOST}/symbols`)
        .then(response => response.json())
        .then((data) => {
          const { response } = data
          setSymbolList(response)
        })
    }, [])
  useEffect(
    () => {
      fetch(`http://${WALLET_ADMIN_HOST}/buy_list`)
        .then(response => response.json())
        .then((data) => {
          const { operations } = data
          setBuyOperations(operations)
        })
    }, [])
  useEffect(
    () => {
      fetch(`http://${WALLET_ADMIN_HOST}/sell_list`)
        .then(response => response.json())
        .then((data) => {
          const { operations } = data
          setSellOperations(operations)
        })
    }, [])
  useEffect(
    () => {
      if (buyOperations && sellOperations) {
        priceChart(buyOperations, sellOperations)
        pieChart(buyOperations, sellOperations)
      }
    }, [buyOperations, sellOperations])

  return (
    <div className='flex items-stretch'>
        {NavMenu()}
        <div className="grid place-items-center h-screen space-y-10">
          <h2 className="text-5xl">Wallet admin</h2>
          {isLoading ? refreshingData() : refreshDataButton()}
          <div className='grid grid-cols-2 gap-2'>
            <div className="p-500">
              <canvas id="priceChart"></canvas>
            </div>
            <div className="p-500">
              <canvas id="pieChart"></canvas>
            </div>
          </div>
          <div className='grid grid-cols-2 gap-8'>
            {buyForm(symbolList)}
            {sellForm(symbolList)}
          </div>
          <div className='grid grid-cols-2 gap-4'>
            <div>
              <table className="table-auto">
                <thead className="bg-white-500 border-b">
                  <tr>
                    <th scope='col' className='font-medium text-center'>Date</th>
                    <th scope='col' className='font-medium text-center'>Symbol</th>
                    <th scope='col' className='font-medium text-center'>Quantity</th>
                    <th scope='col' className='font-medium text-center'>Price per stock $</th>
                    <th scope='col' className='font-medium text-center'>Full price $</th>
                    <th scope='col' className='font-medium text-center'>Final price €</th>
                    <th scope='col' className='font-medium text-center'></th>
                  </tr>
                </thead>
                <tbody>
                  {operationTable(buyOperations, 'buy')}
                </tbody>
              </table>
            </div>
            <div>
              <table className="table-auto">
                <thead className="bg-white-500 border-b">
                  <tr>
                    <th scope='col' className='font-medium text-center'>Date</th>
                    <th scope='col' className='font-medium text-center'>Symbol</th>
                    <th scope='col' className='font-medium text-center'>Quantity</th>
                    <th scope='col' className='font-medium text-center'>Price per stock $</th>
                    <th scope='col' className='font-medium text-center'>Full price $</th>
                    <th scope='col' className='font-medium text-center'>Final price €</th>
                    <th scope='col' className='font-medium text-center'></th>
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
