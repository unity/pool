import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { SmartSearchOverlay } from './SmartSearchOverlay'
import searchIcon from '@/assets/search.svg'

interface SearchTriggerProps {
  apiUrl?: string
  variant?: 'default' | 'floating' | 'minimal'
  className?: string
}

export function SearchTrigger({ 
  apiUrl = 'http://localhost:8000', 
  variant = 'default',
  className = ''
}: SearchTriggerProps) {
  const [search_overlay_open, set_search_overlay_open] = useState(false)

  const open_search = () => set_search_overlay_open(true)
  const close_search = () => set_search_overlay_open(false)

  const render_trigger_button = () => {
    switch (variant) {
      case 'floating':
        return (
          <button
            onClick={open_search}
            className={`w-max fixed bottom-6 right-6 z-40 bg-gradient-to-r from-pink-500 to-purple-600 text-white p-4 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105 ${className}`}
            aria-label="Open beauty search"
          >
             <img src={searchIcon} alt="Search" className="w-6 h-6" />
          </button>
        )
      
      case 'minimal':
        return (
          <button
            onClick={open_search}
            className={`flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors ${className}`}
          >
             <img src={searchIcon} alt="Search" className="w-6 h-6" />
            <span className="text-gray-600 text-sm">Search products...</span>
          </button>
        )
      
      default:
        return (
          <Button
            onClick={open_search}
            className={`w-full rounded-full bg-gradient-to-br from-violet-500 to-violet-700 hover:from-violet-300 hover:to-violet-700 text-white ${className}`}
          >
            <img src={searchIcon} alt="Search" className="w-6 h-6" />
            I'm Liz, ask me anything!
          </Button>
        )
    }
  }

  return (
    <>
      {render_trigger_button()}
      <SmartSearchOverlay 
        isOpen={search_overlay_open}
        onClose={close_search}
        apiUrl={apiUrl}
      />
    </>
  )
} 