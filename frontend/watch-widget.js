import chokidar from 'chokidar'
import { spawn } from 'child_process'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

let buildProcess = null
let buildQueue = false

const build_widget = () => {
  if (buildProcess) {
    console.log('📦 Build already in progress, queuing...')
    buildQueue = true
    return
  }

  console.log('🔨 Building web component...')
  buildProcess = spawn('npm', ['run', 'build:liz'], {
    stdio: 'inherit',
    cwd: __dirname
  })

  buildProcess.on('close', (code) => {
    buildProcess = null
    if (code === 0) {
      console.log('✅ Web component built successfully!')
    } else {
      console.log('❌ Build failed with code:', code)
    }

    if (buildQueue) {
      buildQueue = false
      setTimeout(build_widget, 100) // Small delay to avoid rapid rebuilds
    }
  })
}

// Watch for changes in the webcomponent directory and any related files
const watcher = chokidar.watch([
  'src/webcomponent/**/*.ts',
  'src/webcomponent/**/*.tsx',
  'src/components/**/*.ts',
  'src/components/**/*.tsx',
  'src/assets/**/*',
  'src/lib/**/*.ts'
], {
  ignored: /(^|[\/\\])\../, // ignore dotfiles
  persistent: true,
  ignoreInitial: true
})

watcher
  .on('change', (filepath) => {
    console.log(`📝 File changed: ${filepath}`)
    build_widget()
  })
  .on('add', (filepath) => {
    console.log(`➕ File added: ${filepath}`)
    build_widget()
  })
  .on('unlink', (filepath) => {
    console.log(`➖ File removed: ${filepath}`)
    build_widget()
  })

console.log('👀 Watching for web component changes...')
console.log('📁 Watching directories:')
console.log('  - src/webcomponent/')
console.log('  - src/components/')
console.log('  - src/assets/')
console.log('  - src/lib/')
console.log('')

// Initial build
build_widget() 