const fs = require('fs');
const path = require('path');

// Simple minification function
function minify(code) {
    return code
        .replace(/\/\*[\s\S]*?\*\//g, '') // Remove comments
        .replace(/\s+/g, ' ') // Replace multiple spaces with single space
        .replace(/\s*{\s*/g, '{') // Remove spaces around braces
        .replace(/\s*}\s*/g, '}') // Remove spaces around braces
        .replace(/\s*;\s*/g, ';') // Remove spaces around semicolons
        .replace(/\s*,\s*/g, ',') // Remove spaces around commas
        .replace(/\s*=\s*/g, '=') // Remove spaces around equals
        .replace(/\s*\+\s*/g, '+') // Remove spaces around plus
        .trim();
}

// Build injector
function buildInjector() {
    const injectorSource = fs.readFileSync(path.join(__dirname, 'dist', 'injector.js'), 'utf8');
    const minified = minify(injectorSource);
    fs.writeFileSync(path.join(__dirname, 'dist', 'injector.min.js'), minified);
    console.log('✅ injector.min.js created');
}

// Build widget
function buildWidget() {
    const widgetSource = fs.readFileSync(path.join(__dirname, 'dist', 'widget.js'), 'utf8');
    const minified = minify(widgetSource);
    fs.writeFileSync(path.join(__dirname, 'dist', 'widget.min.js'), minified);
    console.log('✅ widget.min.js created');
}

// Main build function
function build() {
    try {
        console.log('🔨 Building Pool Widget files...\n');
        
        buildInjector();
        buildWidget();
        
        console.log('\n📁 Files created:');
        console.log('   - dist/injector.js (development)');
        console.log('   - dist/injector.min.js (production)');
        console.log('   - dist/widget.js (development)');
        console.log('   - dist/widget.min.js (production)');
        
        console.log('\n🚀 Build completed successfully!');
        console.log('\n📖 Usage:');
        console.log('   1. Include injector.min.js in your HTML');
        console.log('   2. Configure widgetUrl in PoolWidget.config');
        console.log('   3. The injector will load widget.min.js automatically');
        
    } catch (error) {
        console.error('❌ Build failed:', error.message);
        process.exit(1);
    }
}

build(); 