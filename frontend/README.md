# Noli Beauty Search Widget

An AI-powered, embeddable search widget for beauty product recommendations. Designed for the Noli.com platform, this widget provides natural language search capabilities with personalized product recommendations.

## Features

- 🤖 **AI-Powered Search**: Natural language processing for beauty-related queries
- 📱 **Mobile-First Design**: Fullscreen overlay on mobile, responsive on all devices
- 🎨 **Multiple UI Variants**: Floating button, minimal bar, or default button
- 🛍️ **Product Recommendations**: 3-5 curated products with ratings, prices, and explanations
- 🧪 **Quiz Integration**: Call-to-action for more precise recommendations
- 🔧 **Easy Embedding**: Drop-in script for any website

## Quick Start

### 1. Backend Setup

Start the FastAPI backend:

```bash
# From the root directory
poetry install
poetry run uvicorn app.main:app --reload
```

The search endpoint will be available at `http://localhost:8000/api/v1/letta/search`

### 2. Frontend Development

Start the development server:

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to see the demo interface.

## Embedding the Widget

### Method 1: Script Tag (Recommended)

```html
<!-- Floating search button -->
<script 
  src="https://cdn.noli.com/search-widget.js" 
  data-variant="floating"
  data-api-url="https://api.noli.com"
  data-theme="light">
</script>

<!-- Minimal search bar for headers -->
<script 
  src="https://cdn.noli.com/search-widget.js" 
  data-variant="minimal"
  data-container-id="header-search">
</script>

<!-- Default button -->
<script 
  src="https://cdn.noli.com/search-widget.js" 
  data-variant="default"
  data-container-id="search-section">
</script>
```

### Method 2: Programmatic Initialization

```html
<div id="noli-search-widget"></div>

<script src="https://cdn.noli.com/search-widget.js"></script>
<script>
  window.NoliSearch.init({
    containerId: 'noli-search-widget',
    variant: 'floating',
    apiUrl: 'https://api.noli.com',
    theme: 'light'
  });
</script>
```

### Method 3: React Component

```tsx
import { SearchTrigger } from '@noli/beauty-search'

function MyComponent() {
  return (
    <SearchTrigger 
      variant="floating"
      apiUrl="https://api.noli.com"
    />
  )
}
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `variant` | `'floating' \| 'minimal' \| 'default'` | `'floating'` | UI variant of the search trigger |
| `apiUrl` | `string` | `'https://api.noli.com'` | Backend API URL |
| `theme` | `'light' \| 'dark'` | `'light'` | Visual theme |
| `containerId` | `string` | Auto-generated | Container element ID |

## UI Variants

### Floating Button
- **Use case**: Site-wide search availability
- **Position**: Fixed bottom-right corner
- **Behavior**: Opens fullscreen overlay on click

### Minimal Bar
- **Use case**: Navigation headers, search sections
- **Appearance**: Subtle search input style
- **Behavior**: Expands into search overlay

### Default Button
- **Use case**: Call-to-action sections, landing pages
- **Appearance**: Prominent gradient button
- **Behavior**: Opens search overlay

## API Integration

### Search Endpoint

```
POST /api/v1/letta/search
Content-Type: application/json

{
  "query": "products for sensitive dry skin"
}
```

### Response Format

```json
{
  "query": "products for sensitive dry skin",
  "explanation": "For sensitive dry skin, look for gentle, fragrance-free formulations...",
  "products": [
    {
      "id": "prod_001",
      "name": "Hydrating Hyaluronic Acid Serum",
      "brand": "CeraVe",
      "price": 15.99,
      "currency": "USD",
      "rating": 4.7,
      "review_count": 2847,
      "image_url": "/images/cerave-ha-serum.jpg",
      "description": "Lightweight serum that provides 24-hour hydration",
      "why_recommended": "Perfect for dry skin concerns with clinically proven ingredients",
      "learn_more_url": "/products/cerave-ha-serum"
    }
  ],
  "quiz_cta": "Want more precise recommendations? Do the quiz!",
  "quiz_url": "/quiz"
}
```

## Customization

### Styling

The widget uses CSS custom properties for easy theming:

```css
:root {
  --noli-primary-color: #ec4899;
  --noli-secondary-color: #8b5cf6;
  --noli-text-color: #1f2937;
  --noli-background-color: #ffffff;
}
```

### Custom Search Logic

Extend the backend search functionality by modifying:

- `app/api/v1/endpoints/letta.py` - Search endpoint logic
- `app/schemas/letta.py` - Request/response schemas
- Add your own AI service integration

## Mobile Experience

- **Fullscreen overlay** on devices ≤768px width
- **Touch-friendly interactions** with proper tap targets
- **Smooth animations** for overlay transitions
- **Keyboard support** with auto-focus search input

## Example Queries

The widget handles various beauty-related queries:

- "Products for dry sensitive skin"
- "Best anti-aging serums with vitamin C"
- "Gentle cleanser for acne-prone skin"
- "What ingredients help with dark spots?"
- "Moisturizer for oily skin under $30"

## Development

### Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── SmartSearchOverlay.tsx    # Main search interface
│   │   ├── SearchTrigger.tsx         # Trigger button variants
│   │   └── ui/                       # Base UI components
│   ├── widget.tsx                    # Embeddable widget class
│   └── main.tsx                      # Demo application
├── script.js                        # Standalone embeddable script
└── index.html                       # Demo and embedding examples
```

### Backend Structure

```
app/
├── api/v1/endpoints/
│   └── letta.py                      # Search endpoint
├── schemas/
│   └── letta.py                      # API schemas
└── agents/
    └── letta.py                      # AI integration
```

### Building for Production

```bash
# Build the React components
npm run build

# The embeddable script is ready at frontend/script.js
# Deploy both the built assets and script.js to your CDN
```

## Browser Support

- **Modern browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile browsers**: iOS Safari 14+, Chrome Mobile 90+
- **Features**: ES6+, Fetch API, CSS Grid, CSS Custom Properties

## Examples in the Wild

### E-commerce Integration

```html
<!-- Product category pages -->
<div class="category-header">
  <h1>Skincare Products</h1>
  <div id="category-search"></div>
</div>

<script>
  new PoolWidget({
    containerId: 'category-search',
    variant: 'minimal',
    apiUrl: 'https://api.noli.com'
  }).mount()
</script>
```

### Blog/Content Integration

```html
<!-- Beauty blog sidebar -->
<aside class="blog-sidebar">
  <h3>Find Products</h3>
  <div id="blog-search"></div>
</aside>

<script>
  new PoolWidget({
    containerId: 'blog-search',
    variant: 'default',
    apiUrl: 'https://api.noli.com'
  }).mount()
</script>
```

## Support

For technical support or feature requests:

- 📧 **Email**: dev@noli.com
- 📝 **Documentation**: https://docs.noli.com/search-widget
- 🐛 **Issues**: https://github.com/noli/search-widget/issues

## License

MIT License - see LICENSE.md for details.
