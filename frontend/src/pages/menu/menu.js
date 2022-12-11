import React from 'react'

export function NavMenu () {
  return <div className='grow h-14'>
    <aside className="w-64 h-full" aria-label="Sidebar">
     <ul className="space-y-2">
        <li>
           <a href="/" className="flex items-center p-2 text-base font-normal hover:bg-gray-100 dark:hover:bg-gray-500 hover:text-white">
              <span className="ml-3">Wallet Admin</span>
           </a>
        </li>
        <li>
           <a href="stock_information" className="flex items-center p-2 text-base font-normal hover:bg-gray-100 dark:hover:bg-gray-500 hover:text-white">
              <span className="flex-1 ml-3 whitespace-nowrap">Stocks Information</span>
           </a>
        </li>
        <li>
           <a href="recommendations" className="flex items-center p-2 text-base font-normal hover:bg-gray-100 dark:hover:bg-gray-500 hover:text-white">
              <span className="flex-1 ml-3 whitespace-nowrap">Recommendations</span>
           </a>
        </li>
     </ul>
</aside></div>
}
