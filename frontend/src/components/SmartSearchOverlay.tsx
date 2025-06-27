import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import searchIcon from '@/assets/search.svg'

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
  agent_response: string
  agent_id: string
  products: ProductRecommendation[]
  quiz_cta: string
  quiz_url: string
}

interface SmartSearchOverlayProps {
  isOpen: boolean
  onClose: () => void
  apiUrl?: string
}

export function SmartSearchOverlay({ 
  isOpen, 
  onClose, 
  apiUrl = 'http://localhost:8000' 
}: SmartSearchOverlayProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const search_api = async (search_query: string) => {
    if (!search_query.trim()) return

    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${apiUrl}/api/v1/letta/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: search_query })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  const handle_search = (e: React.FormEvent) => {
    e.preventDefault()
    search_api(query)
  }

  const render_star_rating = (rating: number) => {
    const stars = []
    const full_stars = Math.floor(rating)
    const has_half = rating % 1 !== 0

    for (let i = 0; i < full_stars; i++) {
      stars.push(<span key={i} className="text-yellow-400">★</span>)
    }
    
    if (has_half) {
      stars.push(<span key="half" className="text-yellow-400">☆</span>)
    }
    
    const remaining = 5 - Math.ceil(rating)
    for (let i = 0; i < remaining; i++) {
      stars.push(<span key={`empty-${i}`} className="text-gray-300">☆</span>)
    }
    
    return stars
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-50 backdrop-blur-sm">
      <div className="fixed inset-0 md:inset-4 md:max-w-4xl md:mx-auto md:my-8 bg-white md:rounded-lg shadow-xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-violet-50 to-purple-50">
          <h2 className="text-xl font-semibold text-gray-900">Ask Liz 💄</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            aria-label="Close search"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Search Form */}
        <div className="p-4 border-b">
          <form onSubmit={handle_search} className="space-y-4">
            <div className="relative">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="I'm Liz, ask me anything..."
                className="w-full px-4 py-3 pr-10 border border-gray-300 rounded-full focus:ring-2 focus:ring-violet-500 focus:border-transparent text-base"
                autoFocus
              />
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="absolute right-1 top-1/2 transform -translate-y-1/2 p-2 text-violet-600 hover:text-violet-700 rounded-full bg-violet-700 disabled:text-gray-400"
              >
                <img src={searchIcon} alt="Search" className="w-6 h-6" />
              </button>
            </div>
          </form>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6" style={{ maxHeight: 'calc(100vh - 140px)' }}>
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-600"></div>
              <span className="ml-3 text-gray-600">Searching for products...</span>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-700">Error: {error}</p>
            </div>
          )}

          {results && !loading && (
            <>
              {/* Agent Response */}
              <div className="bg-gradient-to-r from-violet-50 to-purple-50 rounded-lg p-6">
                <div className="flex items-center mb-3">
                  <div className="w-8 h-8 bg-violet-500 rounded-full flex items-center justify-center mr-3">
                    <span className="text-white font-bold text-sm">L</span>
                  </div>
                  <h3 className="font-medium text-gray-900">Liz's Beauty Recommendations</h3>
                </div>
                <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {results.agent_response}
                  </ReactMarkdown>
                </div>
              </div>

              {/* Products - Show if available */}
              {results.products && results.products.length > 0 && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-4">Recommended Products</h3>
                  <div className="overflow-x-auto">
                    <div className="flex space-x-4 pb-4" style={{ width: 'max-content' }}>
                      {results.products.map((product) => (
                        <Card key={product.id} className="w-80 flex-shrink-0 hover:shadow-lg transition-shadow">
                          <CardContent className="p-4">
                            <div className="mt-3 aspect-square bg-gray-100 rounded-lg mb-3 flex items-center justify-center">
                              <span className="text-gray-400 text-sm"><img src={product.image_url} alt={product.name} className="w-full h-full object-cover" /></span>
                              
                            </div>
                            
                            <div className="space-y-2">
                              <div>
                                <h4 className="font-medium text-gray-900 line-clamp-2">{product.name}</h4>
                                <p className="text-sm text-gray-600">{product.brand}</p>
                              </div>
                              
                              <div className="flex items-center space-x-2">
                                <div className="flex items-center">
                                  {render_star_rating(product.rating)}
                                </div>
                                <span className="text-sm text-gray-600">({product.review_count})</span>
                              </div>
                              
                              <p className="text-lg font-semibold text-gray-900">
                                ${product.price.toFixed(2)}
                              </p>
                              
                              <p className="text-sm text-gray-600 line-clamp-2">{product.description}</p>
                              
                              <div className="bg-blue-50 rounded-lg p-3">
                                <p className="text-sm text-blue-800">
                                  <strong>Why recommended:</strong> {product.why_recommended}
                                </p>
                              </div>
                              
                              <Button 
                                className="w-full bg-violet-600 hover:bg-violet-700 text-white rounded-full"
                                onClick={() => window.open(product.learn_more_url, '_blank')}
                              >
                                Learn More
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Quiz CTA */}
              <div className="bg-gradient-to-r from-purple-100 to-violet-100 rounded-lg p-6 text-center">
                <h3 className="font-medium text-gray-900 mb-2">{results.quiz_cta}</h3>
                <Button 
                  className="bg-purple-600 hover:bg-purple-700 text-white px-8"
                  onClick={() => window.open(results.quiz_url, '_blank')}
                >
                  Take the Quiz
                </Button>
              </div>
            </>
          )}

          {!results && !loading && !error && (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gradient-to-br from-violet-500 to-violet-700 rounded-full flex items-center justify-center mx-auto mb-4">
                 <img src={searchIcon} alt="Search" className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Search for Beauty Products</h3>
              <p className="text-gray-600 max-w-md mx-auto">
                Ask natural language questions about ingredients, skin concerns, or specific products to get personalized recommendations.
              </p>
              <div className="mt-4 space-y-2 text-sm text-gray-500">
                <p>Try: "Products for dry sensitive skin"</p>
                <p>Or: "Best serums for dark spots"</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 