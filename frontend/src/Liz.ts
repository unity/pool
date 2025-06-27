import searchIcon from '@/assets/search.svg?raw'

interface ProductRecommendation {
  id: string
  name: string
  brand: string
  price: number
  currency: string
  rating: number
  review_count: number
  image_url: string
  description: string
  why_recommended: string
  learn_more_url: string
}

interface SearchResponse {
  query: string
  explanation: string
  products: ProductRecommendation[]
  quiz_cta: string
  quiz_url: string
}

class LizSearchWidget extends HTMLElement {
  private widget_instance: any = null
  private container_id: string
  private shadow: ShadowRoot

  constructor() {
    super()
    
    // Create shadow DOM
    this.shadow = this.attachShadow({ mode: 'open' })
    
    // Generate unique container ID
    this.container_id = `liz-widget-${Math.random().toString(36).substr(2, 9)}`
  }

  private async inject_styles() {
    try {
      // Method 1: Try to import CSS as inline text (works with Vite ?inline)
      try {
        const css_module = await import('./index.css?inline')
        const css_text = css_module.default
        
        const style_element = document.createElement('style')
        style_element.textContent = css_text
        this.shadow.appendChild(style_element)
        return // Success, exit early
      } catch (vite_error) {
        console.log('Vite inline import failed, trying alternative methods')
      }

      // Method 2: Try to fetch the built CSS file
      try {
        const css_files = [
          '/dist/style.css',
          '/dist/index.css',
          './style.css',
          './index.css'
        ]
        
        for (const css_file of css_files) {
          try {
            const response = await fetch(css_file)
            if (response.ok) {
              const css_text = await response.text()
              const style_element = document.createElement('style')
              style_element.textContent = css_text
              this.shadow.appendChild(style_element)
              return // Success, exit early
            }
          } catch (fetch_error) {
            // Continue to next file
          }
        }
      } catch (fetch_error) {
        console.log('CSS fetch failed, trying DOM cloning')
      }

      // Method 3: Clone existing styles from the main document
      const existing_styles = document.querySelectorAll('style, link[rel="stylesheet"]')
      let styles_found = false
      
      existing_styles.forEach(style => {
        if (style.tagName === 'STYLE') {
          const cloned_style = style.cloneNode(true) as HTMLStyleElement
          this.shadow.appendChild(cloned_style)
          styles_found = true
        } else if (style.tagName === 'LINK') {
          const link = style as HTMLLinkElement
          // Clone any stylesheet that might contain our styles
          if (link.href && (
            link.href.includes('index') || 
            link.href.includes('style') ||
            link.href.includes('tailwind') ||
            link.href.includes('.css')
          )) {
            const cloned_link = link.cloneNode(true) as HTMLLinkElement
            this.shadow.appendChild(cloned_link)
            styles_found = true
          }
        }
      })

      if (!styles_found) {
        console.warn('No CSS styles found to inject into shadow DOM')
      }

    } catch (error) {
      console.error('Failed to inject styles into shadow DOM:', error)
    }
  }

  async connectedCallback() {
    try {
      // First inject styles
      await this.inject_styles()
      
      // Then dynamically import the PoolWidget
      const { default: PoolWidget } = await import('./widget')
      
      // Get configuration from attributes
      const api_url = this.getAttribute('api-url') || 'http://localhost:8000'
      const variant = this.getAttribute('variant') || 'default'
      console.log('variant-------', variant)
      const theme = this.getAttribute('theme') || 'light'

      // Create container div inside shadow DOM
      const container = document.createElement('div')
      container.id = this.container_id
      this.shadow.appendChild(container)

      // Create and mount widget inside shadow DOM
      this.widget_instance = new PoolWidget({
        containerId: this.container_id,
        theme: theme as 'light' | 'dark',
        apiUrl: api_url,
        variant: variant as 'default' | 'floating' | 'minimal',
        rootElement: this.shadow // Pass shadow DOM as root
      })

      // Mount the widget with the shadow DOM container
      this.widget_instance.mount()

    } catch (error) {
      console.error('Failed to load Liz widget:', error)
      // Fallback: show a simple error message in shadow DOM
      this.shadow.innerHTML = `
        <div style="
          padding: 16px; 
          background: #fef2f2; 
          border: 1px solid #fecaca; 
          border-radius: 8px; 
          color: #dc2626;
          font-family: system-ui, sans-serif;
        ">
          Failed to load search widget. Please refresh the page.
        </div>
      `
    }
  }

  disconnectedCallback() {
    if (this.widget_instance && typeof this.widget_instance.unmount === 'function') {
      this.widget_instance.unmount()
    }
  }
}

// Register the custom element
customElements.define('liz-search', LizSearchWidget)

// Export for module usage
export default LizSearchWidget 