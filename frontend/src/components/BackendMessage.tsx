import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

interface BackendResponse {
  message: string
}

interface BackendMessageProps {
  apiUrl?: string
}

export function BackendMessage({ apiUrl = 'http://localhost:8000' }: BackendMessageProps) {
  const [message, setMessage] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string>('')

  const fetchMessage = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${apiUrl}/`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data: BackendResponse = await response.json()
      setMessage(data.message)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch message')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMessage()
  }, [apiUrl])

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Backend Connection</CardTitle>
        <CardDescription>
          Message from your FastAPI backend
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {loading && (
          <div className="text-center text-muted-foreground">
            Loading message...
          </div>
        )}
        
        {error && (
          <div className="text-center text-destructive">
            Error: {error}
          </div>
        )}
        
        {message && !loading && !error && (
          <div className="text-center p-4 bg-muted rounded-lg">
            <p className="text-lg font-medium">{message}</p>
          </div>
        )}
        
        <Button 
          onClick={fetchMessage} 
          disabled={loading}
          className="w-full"
        >
          {loading ? 'Loading...' : 'Refresh Message'}
        </Button>
      </CardContent>
    </Card>
  )
} 