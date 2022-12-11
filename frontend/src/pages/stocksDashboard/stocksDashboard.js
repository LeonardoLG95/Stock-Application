import React, { useState, useEffect } from 'react'
import { PULLER_HOST } from '../../constants.js'
import { NavMenu } from '../menu/menu.js'
import { monthlyChart, weeklyChart, dailyChart, resetMonthlyZoom, resetWeeklyZoom, resetDailyZoom } from './components.js'

export function StocksDashboard () {
  const [symbolList, setSymbolList] = useState([])
  const [symbol, setSymbol] = useState('AAPL')
  const [monthlyPrice, setMonthlyPrice] = useState([])
  const [weeklyPrice, setWeeklyPrice] = useState([])
  const [dailyPrice, setDailyPrice] = useState([])

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
      fetch(`http://${PULLER_HOST}/history`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          resolution: 'M'
        })
      })
        .then(response => response.json())
        .then((data) => {
          const { response } = data
          setMonthlyPrice(response)
        })
      fetch(`http://${PULLER_HOST}/history`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          resolution: 'W'
        })
      })
        .then(response => response.json())
        .then((data) => {
          const { response } = data
          setWeeklyPrice(response)
        })
      fetch(`http://${PULLER_HOST}/history`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          resolution: 'D'
        })
      })
        .then(response => response.json())
        .then((data) => {
          const { response } = data
          setDailyPrice(response)
        })
    }, [symbol])

  useEffect(
    () => {
      console.log('Monthly chart is going to change')
      monthlyChart(monthlyPrice, symbol)
    }, [monthlyPrice])

  useEffect(
    () => {
      console.log('Weekly chart is going to change')
      weeklyChart(weeklyPrice, symbol)
    }, [weeklyPrice])

  useEffect(
    () => {
      console.log('Daily chart is going to change')
      dailyChart(dailyPrice, symbol)
    }, [dailyPrice])

  const onStockChange = (e) => {
    setSymbol(e.target.value)
  }

  return (
    <div className='flex'>
      {NavMenu()}
      <div className="grow h-14">
        <div className='space-y-14'>
        <h2 className="text-5xl text-center">Stocks Information</h2>
        <div className='grid grid-cols-3 gap-4'>
          <div>
            <div className='h-96'>
              <canvas id="chartLineDay"></canvas>
            </div>
            {resetDailyZoom()}
          </div>
          <div>
            <div className='h-96'>
            <canvas id="chartLineWeek"></canvas>
            </div>
            {resetWeeklyZoom()}
          </div>
          <div>
            <div className='h-96'>
            <canvas id="chartLineMonth"></canvas>
            </div>
            {resetMonthlyZoom()}
          </div>
        </div>
        </div>
    </div>
    <div className='flex-none w-50 h-14'>
        <form>
        <select placeholder="Symbol" name="symbol" id="symbol" onClick={onStockChange}>
          {symbolList ? symbolList.map(stock => <option value={stock[1]} key={stock[1]}>{stock[0]}</option>) : <option value="null">Not able to load options...</option>}
        </select>
        </form>
      </div>
    </div>
  )
}
