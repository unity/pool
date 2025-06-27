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
  rootElement?: Document | DocumentFragment // Allow custom root for shadow DOM
}

// Extend Window interface to include poolInject
declare global {
  interface Window {
    poolInject?: string
    PoolWidget?: typeof PoolWidget
  }
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
      rootElement: document, // Default to document
      ...config
    }
  }

  mount() {
    // Find or create container using the specified root element
    const root = this.config.rootElement!
    let container = root.getElementById ? root.getElementById(this.config.containerId!) : null
    
    if (!container) {
      container = document.createElement('div')
      container.id = this.config.containerId!
      
      // For floating variant, append to body, otherwise to a designated container
      if (this.config.variant === 'floating') {
        if (root === document) {
          document.body.appendChild(container)
        } else {
          // In shadow DOM, append to the shadow root
          root.appendChild(container)
        }
      } else {
        // Look for a designated injection point or append to body/root
        const injection_point = root.getElementById ? root.getElementById('noli-search-widget') : null
        if (injection_point) {
          injection_point.appendChild(container)
        } else {
          if (root === document) {
            document.body.appendChild(container)
          } else {
            root.appendChild(container)
          }
        }
      }
    }

    this.container = container

    // Apply theme
    if (this.config.theme === 'dark') {
      document.documentElement.classList.add('dark')
    }

    // Create React root and render
    const react_root = createRoot(container)
    react_root.render(
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