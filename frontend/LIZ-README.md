# Liz Beauty Search WebComponent

**Meet Liz** - an AI-powered beauty search assistant packaged as a modern WebComponent for seamless integration into any website. Built for the Noli.com platform, Liz provides intelligent product recommendations through natural language queries.

## 🚀 Quick Start

### 1. Include the Script
```html
<script src="https://cdn.jsdelivr.net/gh/your-repo/frontend/dist/liz-search-widget.js"></script>
```

### 2. Add to Your HTML
```html
<liz-search variant="floating" api-url="https://api.noli.com"></liz-search>
```

**That's it!** Liz is now ready to help your users find beauty products.

## ✨ Features

- 🤖 **AI-Powered Search**: Natural language processing for beauty queries
- 📱 **Mobile-First**: Fullscreen overlay on mobile, responsive everywhere
- 🎨 **Multiple Variants**: Floating button, minimal bar, or default button
- 🛍️ **Rich Product Cards**: Complete product info with ratings and explanations
- 🧪 **Quiz Integration**: Built-in call-to-action for personalized recommendations
- 🔒 **Shadow DOM**: Fully encapsulated styles, no CSS conflicts
- ⚡ **Zero Dependencies**: Pure JavaScript, works everywhere

## 🎯 UI Variants

### Floating Button (`variant="floating"`)
Perfect for site-wide search availability. Appears as a fixed button in the bottom-right corner.

```html
<liz-search variant="floating"></liz-search>
```

**Best for**: E-commerce sites, blogs, any page where users might need product help

### Minimal Bar (`variant="minimal"`)
Subtle search input for headers and navigation areas.

```html
<liz-search variant="minimal"></liz-search>
```

**Best for**: Navigation bars, product category headers, sidebar widgets

### Default Button (`variant="default"`)
Prominent call-to-action for landing pages and main content areas.

```html
<liz-search variant="default"></liz-search>
```

**Best for**: Landing pages, product pages, main content sections

## ⚙️ Configuration

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `variant` | `"floating"` \| `"minimal"` \| `"default"` | `"floating"` | UI variant |
| `api-url` | `string` | `"http://localhost:8000"` | Backend API endpoint |
| `theme` | `"light"` \| `"dark"` | `"light"` | Visual theme (future) |

### Example with all options:
```html
<liz-search 
  variant="floating"
  api-url="https://api.noli.com"
  theme="light">
</liz-search>
```

## 📱 Mobile Experience

Liz automatically adapts to mobile devices:
- **Fullscreen overlay** on screens ≤768px width
- **Touch-friendly** interactions with proper tap targets
- **Smooth animations** for overlay transitions
- **Auto-focus** on search input for immediate typing

## 🔍 Search Capabilities

Liz understands natural language queries about:

### Skin Concerns
- "Products for dry sensitive skin"
- "Best moisturizer for oily skin"
- "Anti-aging routine for mature skin"

### Specific Ingredients
- "Serums with vitamin C"
- "Retinol products for beginners"
- "Hyaluronic acid moisturizers"

### Product Types
- "Gentle cleanser for acne-prone skin"
- "Sunscreen under $25"
- "Night cream for combination skin"

### Beauty Goals
- "How to reduce dark spots"
- "Best products for glowing skin"
- "Makeup primer for large pores"

## 💻 Integration Examples

### E-commerce Header
```html
<header class="site-header">
  <nav class="navigation">
    <div class="logo">Noli</div>
    <div class="search-container">
      <liz-search variant="minimal"></liz-search>
    </div>
    <div class="nav-links">...</div>
  </nav>
</header>
```

### Product Category Page
```html
<div class="category-page">
  <div class="category-header">
    <h1>Skincare Products</h1>
    <p class="category-description">Discover your perfect skincare routine</p>
    <liz-search variant="default"></liz-search>
  </div>
  <!-- Product grid -->
</div>
```

### Blog Sidebar
```html
<aside class="blog-sidebar">
  <div class="widget">
    <h3>Find Products</h3>
    <p>Ask Liz about any beauty concern</p>
    <liz-search variant="default"></liz-search>
  </div>
</aside>
```

### Global Search (Floating)
```html
<!-- Anywhere in your HTML -->
<liz-search variant="floating" api-url="https://api.noli.com"></liz-search>
```

## 🎨 Customization

### CSS Custom Properties
While Liz uses Shadow DOM to avoid conflicts, you can customize colors via CSS custom properties:

```css
liz-search {
  --liz-primary: #your-brand-color;
  --liz-secondary: #your-secondary-color;
}
```

### Available Properties
```css
:root {
  --liz-primary: #ec4899;      /* Primary brand color */
  --liz-secondary: #8b5cf6;    /* Secondary brand color */
  --liz-text: #1f2937;         /* Text color */
  --liz-bg: #ffffff;           /* Background color */
  --liz-border: #e5e7eb;       /* Border color */
  --liz-shadow: 0 10px 25px rgba(0,0,0,0.15); /* Shadow */
}
```

## 🔧 Development

### Backend Requirements
Liz requires a backend endpoint that accepts search queries:

```
POST /api/v1/letta/search
Content-Type: application/json

{
  "query": "products for dry skin"
}
```

### Response Format
```json
{
  "query": "products for dry skin",
  "explanation": "For dry skin, focus on hydrating ingredients...",
  "products": [
    {
      "id": "prod_001",
      "name": "Hydrating Serum",
      "brand": "CeraVe",
      "price": 15.99,
      "currency": "USD",
      "rating": 4.7,
      "review_count": 2847,
      "image_url": "/images/product.jpg",
      "description": "Lightweight hydrating serum",
      "why_recommended": "Perfect for dry skin with proven ingredients",
      "learn_more_url": "/products/hydrating-serum"
    }
  ],
  "quiz_cta": "Want more precise recommendations? Do the quiz!",
  "quiz_url": "/quiz"
}
```

### Building from Source
```bash
cd frontend
npm install
npm run build:liz
```

This creates `dist/liz-search-widget.js` ready for distribution.

## 🌍 Browser Support

- **Modern Browsers**: Chrome 67+, Firefox 63+, Safari 10.1+, Edge 79+
- **Mobile**: iOS Safari 10.3+, Chrome Mobile 67+
- **Features Used**: Custom Elements, Shadow DOM, Fetch API, ES6+

## 🔒 Security & Privacy

- **Shadow DOM**: Complete style isolation, no CSS leakage
- **No External Dependencies**: Self-contained, no third-party scripts
- **HTTPS Ready**: Secure API communication
- **No Data Storage**: No localStorage or cookies used

## 📈 Analytics Integration

Track Liz usage with your analytics platform:

```javascript
// Listen for search events
document.addEventListener('liz-search', (event) => {
  analytics.track('Beauty Search', {
    query: event.detail.query,
    variant: event.detail.variant
  });
});
```

## 🚀 CDN Hosting

### jsDelivr (Recommended)
```html
<script src="https://cdn.jsdelivr.net/gh/noli/search-widget@latest/dist/liz-search-widget.js"></script>
```

### unpkg
```html
<script src="https://unpkg.com/@noli/liz-search@latest/dist/liz-search-widget.js"></script>
```

### Self-Hosted
Download `liz-search-widget.js` and host on your own CDN:
```html
<script src="https://your-cdn.com/js/liz-search-widget.js"></script>
```

## 🤝 Support & Contributing

### Issues & Bug Reports
- 📧 **Email**: dev@noli.com
- 🐛 **GitHub Issues**: [Report a bug](https://github.com/noli/search-widget/issues)

### Feature Requests
- 💡 **Discussions**: [Feature requests](https://github.com/noli/search-widget/discussions)
- 📝 **Documentation**: [docs.noli.com](https://docs.noli.com/liz-widget)

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with the demo page
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE.md](LICENSE.md) for details.

---

## 🎪 Try the Demo

Want to see Liz in action? Check out our [interactive demo](./liz-demo.html):

```bash
# Clone this repo
git clone https://github.com/noli/search-widget
cd frontend

# Open the demo
open liz-demo.html
# or serve locally
python -m http.server 8080
```

## 💡 Pro Tips

### Performance
- Load Liz asynchronously to avoid blocking page render
- Use the floating variant for global availability
- Implement proper error handling for API failures

### UX Best Practices
- Place minimal variants in expected search locations
- Use default buttons as clear calls-to-action
- Provide example queries to guide users

### SEO Considerations
- Liz doesn't interfere with page content or SEO
- Consider adding a fallback search form for non-JS users
- Use structured data for your product pages

---

**Liz** - Making beauty product discovery intelligent, intuitive, and effortless. 💄✨ 