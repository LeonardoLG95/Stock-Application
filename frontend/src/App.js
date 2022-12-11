import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { WalletEvolution } from './pages/wallet/wallet.js'
import { StocksDashboard } from './pages/stocksDashboard/stocksDashboard.js'
import { Recommendations } from './pages/recommendations/recommendations.js'

function App () {
  return <BrowserRouter>
          <Routes>
            <Route path="/" element={< WalletEvolution />}/>
            <Route path="stock_information" element={< StocksDashboard />}/>
            <Route path="recommendations" element={< Recommendations />}/>
          </Routes>
        </BrowserRouter>
}

export default App
