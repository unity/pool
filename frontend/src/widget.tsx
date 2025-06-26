import React from 'react'
import { createRoot } from 'react-dom/client'
import { SearchTrigger } from './components/SearchTrigger'
import './index.css'

// Widget configuration interface
interface PoolWidgetConfig {
  containerId?: string
  theme?: 'light' | 'dark'
  apiUrl?: string
  variant?: 'default' | 'floating' | 'minimal'
}

window.poolInject = window.poolInject || 'poolContainer'

class PoolWidget {
  private config: PoolWidgetConfig
  private container: HTMLElement | null = null

  constructor(config: PoolWidgetConfig = {}) {
    this.config = {
      containerId: 'pool-widget-container',
      theme: 'light',
      apiUrl: 'http://localhost:8000',
      variant: 'floating',
      ...config
    }
  }

  mount() {
    // Find or create container
    let container = document.getElementById(this.config.containerId!)
    if (!container) {
      container = document.createElement('div')
      container.id = this.config.containerId!
      
      // For floating variant, append to body, otherwise to a designated container
      if (this.config.variant === 'floating') {
        document.body.appendChild(container)
      } else {
        // Look for a designated injection point or append to body
        const injection_point = document.getElementById('noli-search-widget')
        if (injection_point) {
          injection_point.appendChild(container)
        } else {
          document.body.appendChild(container)
        }
      }
    }

    this.container = container

    // Apply theme
    if (this.config.theme === 'dark') {
      document.documentElement.classList.add('dark')
    }

    // Create React root and render
    const root = createRoot(container)
    root.render(
      <React.StrictMode>
        <div className="noli-beauty-search-widget">
          <SearchTrigger 
            apiUrl={this.config.apiUrl}
            variant={this.config.variant}
          />
        </div>
      </React.StrictMode>
    )
  }

  unmount() {
    if (this.container) {
      const root = createRoot(this.container)
      root.unmount()
      this.container.remove()
      this.container = null
    }
  }
}

// Auto-initialize if script is loaded directly
if (typeof window !== 'undefined') {
  // @ts-ignore
  window.PoolWidget = PoolWidget
  
  // Auto-mount if data attributes are present
  const script = document.currentScript as HTMLScriptElement
  if (script) {
    const containerId = script.getAttribute('data-container-id')
    const theme = script.getAttribute('data-theme') as 'light' | 'dark'
    const apiUrl = script.getAttribute('data-api-url')
    const variant = script.getAttribute('data-variant') as 'default' | 'floating' | 'minimal'
    
    if (containerId || theme || apiUrl || variant) {
      const widget = new PoolWidget({
        containerId: containerId || undefined,
        theme: theme || undefined,
        apiUrl: apiUrl || undefined,
        variant: variant || undefined
      })
      widget.mount()
    }
  }
}

export default PoolWidget 