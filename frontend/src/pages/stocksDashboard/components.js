import React from 'react'
import Chart from 'chart.js/auto'
// import { PULLER_HOST } from '../../constants.js'
import zoomPlugin from 'chartjs-plugin-zoom'

Chart.register(zoomPlugin)

function parseChartConfig (history, symbol) {
  const time = []
  history.forEach(e => time.push(e[0]))
  for (let i = 0; i < time.length; i++) {
    const pad = (s) => { return (s < 10) ? '0' + s : s }
    const date = new Date(time[i])
    time[i] = [pad(date.getDate()), pad(date.getMonth() + 1), date.getFullYear()].join('-')
  }

  const price = []
  history.forEach(e => price.push(e[1]))

  return {
    type: 'line',
    data: {
      labels: time,
      datasets: [{
        label: `${symbol}`,
        data: price,
        borderColor: 'rgba(0, 0, 0, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        zoom: {
          zoom: {
            drag: {
              enabled: true
            },
            mode: 'xy'
          }
        }
      }
    }
  }
}

export function monthlyChart (history, symbol) {
  const config = parseChartConfig(history, symbol)
  const canvas = document.getElementById('chartLineMonth').getContext('2d')
  if (window.monthlyCloseChart) {
    window.monthlyCloseChart.destroy()
  }
  window.monthlyCloseChart = new Chart(canvas, config)
}

export function resetMonthlyZoom () {
  const resetZoom = (e) => {
    e.preventDefault()
    if (window.monthlyCloseChart) {
      window.monthlyCloseChart.resetZoom()
    }
  }

  return <form onSubmit={resetZoom}>
    <input className="bg-gray-500 hover:bg-gray-400 text-white font-bold py-2 px-4 rounded" type="submit" value="Reset zoom"></input>
  </form>
}

export function weeklyChart (history, symbol) {
  const config = parseChartConfig(history, symbol)
  const canvas = document.getElementById('chartLineWeek').getContext('2d')
  if (window.weeklyCloseChart) {
    window.weeklyCloseChart.destroy()
  }
  window.weeklyCloseChart = new Chart(canvas, config)
}

export function resetWeeklyZoom () {
  const resetZoom = (e) => {
    e.preventDefault()
    if (window.weeklyCloseChart) {
      window.weeklyCloseChart.resetZoom()
    }
  }

  return <form onSubmit={resetZoom}>
    <input className="bg-gray-500 hover:bg-gray-400 text-white font-bold py-2 px-4 rounded" type="submit" value="Reset zoom"></input>
  </form>
}

export function dailyChart (history, symbol) {
  const config = parseChartConfig(history, symbol)
  const canvas = document.getElementById('chartLineDay').getContext('2d')
  if (window.dailyCloseChart) {
    window.dailyCloseChart.destroy()
  }
  window.dailyCloseChart = new Chart(canvas, config)
}

export function resetDailyZoom () {
  const resetZoom = (e) => {
    e.preventDefault()
    if (window.dailyCloseChart) {
      window.dailyCloseChart.resetZoom()
    }
  }

  return <form onSubmit={resetZoom}>
    <input className="bg-gray-500 hover:bg-gray-400 text-white font-bold py-2 px-4 rounded" type="submit" value="Reset zoom"></input>
  </form>
}
