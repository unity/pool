# Pool Widget Injector

A lightweight JavaScript widget that can be injected into any website to display content from your FastAPI backend.

## Features

- 🚀 **Lightweight**: No dependencies, pure vanilla JavaScript
- 🔧 **Configurable**: Customize backend URL, container ID, styling
- 🎨 **Self-contained**: Includes all necessary CSS styles
- 🔄 **Interactive**: Refresh button to fetch latest data
- 🛡️ **Error handling**: Graceful error display
- 📱 **Responsive**: Works on desktop and mobile

## Quick Start

### 1. Include the Script

Add this to your HTML `<head>` or before the closing `</body>` tag:

```html
<script src="https://your-domain.com/injector.min.js"></script>
```

### 2. Configure (Optional)

Customize the widget before it loads:

```html
<script>
window.PoolWidget = {
    config: {
        backendUrl: 'https://your-backend.com',
        containerId: 'my-widget-container',
        width: '100%',
        height: 'auto',
        minHeight: '400px'
    }
};
</script>
```

### 3. Widget Auto-injects

The widget will automatically create a container and inject itself into the page.

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `backendUrl` | string | `'http://localhost:8000'` | URL of your FastAPI backend |
| `containerId` | string | `'pool-widget-container'` | ID of the container element |
| `theme` | string | `'light'` | Theme (currently only 'light' supported) |
| `width` | string | `'100%'` | Widget width |
| `height` | string | `'auto'` | Widget height |
| `minHeight` | string | `'400px'` | Minimum widget height |

## JavaScript API

Once loaded, you can control the widget programmatically:

### Refresh the widget
```javascript
window.PoolWidget.api.refresh();
```

### Update configuration
```javascript
window.PoolWidget.api.setConfig({
    backendUrl: 'https://new-backend.com',
    width: '500px'
});
```

### Remove the widget
```javascript
window.PoolWidget.api.destroy();
```

## Backend Requirements

Your FastAPI backend should have an endpoint that returns JSON in this format:

```json
{
    "message": "Your message here"
}
```

Example FastAPI endpoint:
```python
@app.get("/")
async def root():
    return {"message": "Welcome to Pool Backend API"}
```

## Building

To build the injector:

```bash
cd frontend
npm run build:injector
```

This creates:
- `dist/injector.js` - Development version
- `dist/injector.min.js` - Minified production version

## Example Integration

See `example.html` for a complete working example.

## Styling

The widget is self-contained with its own CSS. It uses a clean, modern design that should work well on most websites. The styling is applied inline to avoid conflicts with the host page's CSS.

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Security Considerations

- The widget makes CORS requests to your backend
- Ensure your backend has proper CORS headers configured
- Consider rate limiting on your backend endpoints
- The widget runs in the same context as the host page

## Troubleshooting

### Widget not appearing
- Check browser console for JavaScript errors
- Ensure the script is loaded before the page finishes loading
- Verify the backend URL is accessible

### CORS errors
- Configure CORS on your backend to allow requests from the widget's domain
- Add your domain to the allowed origins

### Styling conflicts
- The widget uses inline styles to avoid conflicts
- If you need custom styling, modify the `injector.js` file

## License

This widget is part of the Pool project and follows the same license terms. 