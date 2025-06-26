import { BackendMessage } from './components/BackendMessage'

function App() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold tracking-tight mb-2">
            Pool Frontend
          </h1>
          <p className="text-muted-foreground">
            React + TypeScript + shadcn/ui + FastAPI Backend
          </p>
        </div>
        
        <BackendMessage />
        
        <div className="mt-8 text-center text-sm text-muted-foreground">
          <p>
            Make sure your FastAPI backend is running on{' '}
            <code className="bg-muted px-1 py-0.5 rounded">http://localhost:8000</code>
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
