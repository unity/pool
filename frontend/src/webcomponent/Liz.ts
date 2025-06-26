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
  private shadow: ShadowRoot
  private api_url: string
  private variant: string
  private theme: string
  private is_overlay_open = false

  constructor() {
    super()
    this.shadow = this.attachShadow({ mode: 'open' })
    
    // Get configuration from attributes
    this.api_url = this.getAttribute('api-url') || 'http://localhost:8000'
    this.variant = this.getAttribute('variant') || 'floating'
    this.theme = this.getAttribute('theme') || 'light'
  }

  connectedCallback() {
    this.render()
    this.attach_event_listeners()
  }

  private render() {
    this.shadow.innerHTML = `
      ${this.get_styles()}
      <div class="liz-container">
        ${this.get_trigger_html()}
      </div>
    `
  }

  private get_styles() {
    return `
      <style>
        :host {
          --liz-primary: #ec4899;
          --liz-secondary: #8b5cf6;
          --liz-text: #1f2937;
          --liz-bg: #ffffff;
          --liz-border: #e5e7eb;
          --liz-shadow: 0 10px 25px rgba(0,0,0,0.15);
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .liz-container {
          position: relative;
          display: flex;
          justify-content: center;
          align-items: center;
          width: 100%;
          height: 100%;
        }

        .liz-trigger-floating {
          position: fixed;
          bottom: 24px;
          right: 24px;
          z-index: 9999;
          background: linear-gradient(135deg, var(--liz-primary) 0%, var(--liz-secondary) 100%);
          color: white;
          border: none;
          border-radius: 50%;
          width: 64px;
          height: 64px;
          box-shadow: var(--liz-shadow);
          cursor: pointer;
          transition: all 0.2s ease;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .liz-trigger-floating:hover {
          transform: scale(1.05);
          box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        }

        .liz-trigger-minimal {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          background: #f3f4f6;
          border: 1px solid var(--liz-border);
          border-radius: 8px;
          cursor: pointer;
          transition: background-color 0.2s ease;
          font-size: 14px;
          color: #6b7280;
        }

        .liz-trigger-minimal:hover {
          background: #e5e7eb;
        }

        .liz-trigger-default {
          background: linear-gradient(135deg, var(--liz-primary) 0%, var(--liz-secondary) 100%);
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 8px;
          transition: all 0.2s ease;
          flex-grow: 1;
          margin: 1rem 1rem;
          justify-content: center;
          display: flex;

          appearance: none;
          align-items: center;
          justify-content: center;
          user-select: none;
          position: relative;
          white-space: nowrap;
          vertical-align: middle;
          outline: 2px solid transparent;
          outline-offset: 2px;
          line-height: var(--chakra-lineHeights-4);
          border-radius: var(--chakra-radii-full);
          font-weight: var(--chakra-fontWeights-semibold);
          transition-property: var(--chakra-transition-property-common);
          transition-duration: var(--chakra-transition-duration-normal);
          height: var(--chakra-sizes-16);
          min-width: fit-content;
          font-size: var(--chakra-fontSizes-sm);
          padding-inline-start: var(--chakra-space-6);
          padding-inline-end: var(--chakra-space-6);
          gap: var(--chakra-space-2);
          color: var(--chakra-colors-primary-white);
          background-image: linear-gradient(to bottom left, var(--chakra-colors-bdna-bdna-20), var(--chakra-colors-bdna-bdna-100));
          animation: animation-xhr65c 8s ease infinite;
          background-size: 400% 400%;
          flex: 1;
          flex-grow: 1;
          }

        .liz-trigger-default:hover {
          background: linear-gradient(135deg, #db2777 0%, #7c3aed 100%);
          transform: translateY(-1px);
        }

        .liz-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          width: 100vw;
          height: 100vh;
          background: rgba(0,0,0,0.5);
          backdrop-filter: blur(4px);
          z-index: 10000;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 16px;
          animation: liz-fade-in 0.2s ease-out;
        }

        .liz-modal {
          background: var(--liz-bg);
          border-radius: 12px;
          width: 100%;
          max-width: 800px;
          max-height: 90vh;
          overflow: hidden;
          box-shadow: 0 25px 50px rgba(0,0,0,0.25);
          animation: liz-slide-up 0.3s ease-out;
        }

        .liz-header {
          padding: 20px;
          border-bottom: 1px solid var(--liz-border);
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: linear-gradient(135deg, #fdf2f8 0%, #f3e8ff 100%);
        }

        .liz-title {
          margin: 0;
          font-size: 20px;
          font-weight: 600;
          color: var(--liz-text);
        }

        .liz-close {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          padding: 8px;
          border-radius: 4px;
          color: #6b7280;
        }

        .liz-close:hover {
          background: #f3f4f6;
        }

        .liz-search-form {
          padding: 20px;
          border-bottom: 1px solid var(--liz-border);
        }

        .liz-search-input-container {
          position: relative;
        }

        .liz-search-input {
          width: 100%;
          padding: 12px 16px;
          border: 2px solid var(--liz-border);
          border-radius: 8px;
          font-size: 16px;
          outline: none;
          box-sizing: border-box;
        }

        .liz-search-input:focus {
          border-color: var(--liz-primary);
          box-shadow: 0 0 0 3px rgba(236, 72, 153, 0.1);
        }

        .liz-search-button {
          position: absolute;
          right: 8px;
          top: 50%;
          transform: translateY(-50%);
          background: none;
          border: none;
          color: var(--liz-primary);
          cursor: pointer;
          padding: 8px;
        }

        .liz-content {
          padding: 20px;
          max-height: 70vh;
          overflow-y: auto;
        }

        .liz-loading {
          text-align: center;
          padding: 40px;
          color: #6b7280;
        }

        .liz-spinner {
          display: inline-block;
          width: 24px;
          height: 24px;
          border: 2px solid #e5e7eb;
          border-top-color: var(--liz-primary);
          border-radius: 50%;
          animation: liz-spin 0.8s linear infinite;
          margin-right: 12px;
        }

        .liz-error {
          background: #fef2f2;
          border: 1px solid #fecaca;
          color: #dc2626;
          padding: 16px;
          border-radius: 8px;
          text-align: center;
        }

        .liz-explanation {
          background: linear-gradient(135deg, #fdf2f8 0%, #f3e8ff 100%);
          padding: 16px;
          border-radius: 8px;
          margin-bottom: 20px;
        }

        .liz-explanation h3 {
          margin: 0 0 8px 0;
          font-weight: 600;
          color: var(--liz-text);
        }

        .liz-explanation p {
          margin: 0;
          line-height: 1.5;
          color: #374151;
        }

        .liz-products-title {
          margin: 0 0 16px 0;
          font-weight: 600;
          color: var(--liz-text);
        }

        .liz-products-container {
          overflow-x: auto;
          margin-bottom: 20px;
        }

        .liz-products-grid {
          display: flex;
          gap: 16px;
          min-width: max-content;
          padding-bottom: 8px;
        }

        .liz-product-card {
          border: 1px solid var(--liz-border);
          border-radius: 8px;
          padding: 16px;
          width: 320px;
          flex-shrink: 0;
          transition: all 0.2s ease;
        }

        .liz-product-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }

        .liz-product-image {
          width: 100%;
          height: 120px;
          background: #f3f4f6;
          border-radius: 8px;
          margin-bottom: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #6b7280;
          font-size: 14px;
        }

        .liz-product-name {
          margin: 0 0 4px 0;
          font-weight: 600;
          color: var(--liz-text);
          font-size: 16px;
        }

        .liz-product-brand {
          margin: 0 0 8px 0;
          color: #6b7280;
          font-size: 14px;
        }

        .liz-product-rating {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
        }

        .liz-stars {
          color: #fbbf24;
        }

        .liz-review-count {
          font-size: 14px;
          color: #6b7280;
        }

        .liz-product-price {
          margin: 0 0 8px 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--liz-text);
        }

        .liz-product-description {
          margin: 0 0 12px 0;
          font-size: 14px;
          color: #6b7280;
          line-height: 1.4;
        }

        .liz-product-why {
          background: #dbeafe;
          padding: 8px;
          border-radius: 6px;
          margin-bottom: 12px;
          font-size: 13px;
          color: #1e40af;
        }

        .liz-product-cta {
          background: var(--liz-primary);
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          width: 100%;
          transition: background-color 0.2s ease;
        }

        .liz-product-cta:hover {
          background: #db2777;
        }

        .liz-quiz-section {
          background: linear-gradient(135deg, #e0e7ff 0%, #fce7f3 100%);
          padding: 20px;
          border-radius: 8px;
          text-align: center;
        }

        .liz-quiz-title {
          margin: 0 0 12px 0;
          font-weight: 600;
          color: var(--liz-text);
        }

        .liz-quiz-button {
          background: var(--liz-secondary);
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 500;
          transition: background-color 0.2s ease;
        }

        .liz-quiz-button:hover {
          background: #7c3aed;
        }

        .liz-empty-state {
          text-align: center;
          padding: 40px;
        }

        .liz-empty-icon {
          width: 64px;
          height: 64px;
          background: linear-gradient(135deg, #fdf2f8 0%, #f3e8ff 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 16px;
          color: var(--liz-primary);
        }

        .liz-empty-title {
          margin: 0 0 8px 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--liz-text);
        }

        .liz-empty-description {
          margin: 0 0 16px 0;
          color: #6b7280;
          max-width: 300px;
          margin-left: auto;
          margin-right: auto;
        }

        .liz-empty-examples {
          font-size: 14px;
          color: #9ca3af;
        }

        .liz-empty-examples p {
          margin: 4px 0;
        }

        @keyframes liz-fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes liz-slide-up {
          from {
            transform: translateY(20px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }

        @keyframes liz-spin {
          to { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .liz-modal {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            max-width: none !important;
            max-height: none !important;
            border-radius: 0 !important;
            margin: 0 !important;
          }

          .liz-products-grid {
            flex-direction: column;
            min-width: auto;
          }

          .liz-product-card {
            width: 100%;
          }
        }
      </style>
    `
  }

  private get_trigger_html() {
    switch (this.variant) {
      case 'floating':
        return `<button class="liz-trigger-floating" title="Search beauty products">${searchIcon}</button>`
      case 'minimal':
        return `<button class="liz-trigger-minimal">${searchIcon} Search products...</button>`
      default:
        return `<button class="liz-trigger-default">${searchIcon} Search Beauty Products</button>`
    }
  }

  private attach_event_listeners() {
    const trigger = this.shadow.querySelector('.liz-trigger-floating, .liz-trigger-minimal, .liz-trigger-default')
    trigger?.addEventListener('click', () => this.open_search())
  }

  private open_search() {
    if (this.is_overlay_open) return
    this.is_overlay_open = true

    const overlay = document.createElement('div')
    overlay.className = 'liz-overlay'
    overlay.innerHTML = `
      <div class="liz-modal">
        <div class="liz-header">
          <h2 class="liz-title">Beauty Search by Liz</h2>
          <button class="liz-close">&times;</button>
        </div>
        <div class="liz-search-form">
          <div class="liz-search-input-container">
            <input 
              type="text" 
              class="liz-search-input" 
              placeholder="Ask about ingredients, skin concerns, or specific products..."
              autocomplete="off"
            />
            <button class="liz-search-button" type="submit">
              <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
            </button>
          </div>
        </div>
        <div class="liz-content">
          ${this.get_empty_state_html()}
        </div>
      </div>
    `

    // Add to shadow DOM to ensure styles are applied
    this.shadow.appendChild(overlay)

    // Event listeners
    const close_button = overlay.querySelector('.liz-close')
    close_button?.addEventListener('click', () => this.close_search(overlay))

    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) this.close_search(overlay)
    })

    const search_input = overlay.querySelector('.liz-search-input') as HTMLInputElement
    const search_button = overlay.querySelector('.liz-search-button')

    const perform_search = () => {
      const query = search_input.value.trim()
      if (query) this.search(query, overlay)
    }

    search_button?.addEventListener('click', perform_search)
    search_input?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') perform_search()
    })

    // Focus input
    setTimeout(() => search_input?.focus(), 100)
  }

  private close_search(overlay: Element) {
    this.shadow.removeChild(overlay)
    this.is_overlay_open = false
  }

  private async search(query: string, overlay: Element) {
    const content = overlay.querySelector('.liz-content')
    if (!content) return

    // Show loading state
    content.innerHTML = `
      <div class="liz-loading">
        <div class="liz-spinner"></div>
        Searching for products...
      </div>
    `

    try {
      const response = await fetch(`${this.api_url}/api/v1/letta/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      })

      if (!response.ok) throw new Error('Search failed')

      const data: SearchResponse = await response.json()
      this.render_search_results(data, content)

    } catch (error) {
      content.innerHTML = `
        <div class="liz-error">
          Search failed. Please try again.
        </div>
      `
    }
  }

  private render_search_results(data: SearchResponse, content: Element) {
    const products_html = data.products.map(product => `
      <div class="liz-product-card">
        <div class="liz-product-image">
          Product Image
        </div>
        <h4 class="liz-product-name">${product.name}</h4>
        <p class="liz-product-brand">${product.brand}</p>
        <div class="liz-product-rating">
          <div class="liz-stars">${this.render_stars(product.rating)}</div>
          <span class="liz-review-count">(${product.review_count})</span>
        </div>
        <p class="liz-product-price">$${product.price.toFixed(2)}</p>
        <p class="liz-product-description">${product.description}</p>
        <div class="liz-product-why">
          <strong>Why recommended:</strong> ${product.why_recommended}
        </div>
        <button class="liz-product-cta" onclick="window.open('${product.learn_more_url}', '_blank')">
          Learn More
        </button>
      </div>
    `).join('')

    content.innerHTML = `
      <div class="liz-explanation">
        <h3>Here's what we found:</h3>
        <p>${data.explanation}</p>
      </div>
      
      <h3 class="liz-products-title">Recommended Products</h3>
      <div class="liz-products-container">
        <div class="liz-products-grid">
          ${products_html}
        </div>
      </div>
      
      <div class="liz-quiz-section">
        <h3 class="liz-quiz-title">${data.quiz_cta}</h3>
        <button class="liz-quiz-button" onclick="window.open('${data.quiz_url}', '_blank')">
          Take the Quiz
        </button>
      </div>
    `
  }

  private render_stars(rating: number) {
    const full_stars = Math.floor(rating)
    const has_half = rating % 1 !== 0
    let stars = ''

    for (let i = 0; i < full_stars; i++) {
      stars += '★'
    }
    
    if (has_half) stars += '☆'
    
    const remaining = 5 - Math.ceil(rating)
    for (let i = 0; i < remaining; i++) {
      stars += '☆'
    }
    
    return stars
  }

  private get_empty_state_html() {
    return `
      <div class="liz-empty-state">
        <div class="liz-empty-icon">
          <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
        <h3 class="liz-empty-title">Search for Beauty Products</h3>
        <p class="liz-empty-description">
          Ask natural language questions about ingredients, skin concerns, or specific products to get personalized recommendations.
        </p>
        <div class="liz-empty-examples">
          <p>Try: "Products for dry sensitive skin"</p>
          <p>Or: "Best serums for dark spots"</p>
        </div>
      </div>
    `
  }
}

// Register the custom element
customElements.define('liz-search', LizSearchWidget)

// Export for module usage
export default LizSearchWidget 