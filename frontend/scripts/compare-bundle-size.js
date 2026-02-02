#!/usr/bin/env node

/**
 * Compare Bundle Sizes - Track bundle size changes during DDD migration
 *
 * This script:
 * 1. Takes a baseline bundle size measurement
 * 2. Compares current bundle with baseline
 * 3. Alerts if bundle grows more than 10%
 * 4. Tracks metrics for migration dashboard
 *
 * Usage:
 *   node scripts/compare-bundle-size.js --baseline  (create baseline)
 *   node scripts/compare-bundle-size.js --check     (compare with baseline)
 *   node scripts/compare-bundle-size.js --report    (show migration progress)
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import { execSync } from 'child_process'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

const args = process.argv.slice(2)
const action = args[0] || '--check'

const metricsDir = path.resolve(__dirname, '../.migration-metrics')
const baselineFile = path.join(metricsDir, 'bundle-baseline.json')
const historyFile = path.join(metricsDir, 'bundle-history.json')

// Ensure metrics directory exists
if (!fs.existsSync(metricsDir)) {
  fs.mkdirSync(metricsDir, { recursive: true })
}

function getDistSize() {
  const distPath = path.resolve(__dirname, '../dist')

  if (!fs.existsSync(distPath)) {
    console.error('❌ dist/ directory not found. Please run: npm run build')
    process.exit(1)
  }

  let totalSize = 0

  function traverse(dir) {
    const files = fs.readdirSync(dir)
    files.forEach(file => {
      const fullPath = path.join(dir, file)
      const stat = fs.statSync(fullPath)

      if (stat.isDirectory()) {
        traverse(fullPath)
      } else {
        totalSize += stat.size
      }
    })
  }

  traverse(distPath)
  return totalSize
}

function formatBytes(bytes) {
  return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}

function getChunks() {
  const distPath = path.resolve(__dirname, '../dist')
  const chunks = {}

  if (!fs.existsSync(distPath)) {
    return chunks
  }

  const files = fs.readdirSync(distPath)
  files.forEach(file => {
    if (file.endsWith('.js') || file.endsWith('.css')) {
      const fullPath = path.join(distPath, file)
      const size = fs.statSync(fullPath).size
      chunks[file] = size
    }
  })

  return chunks
}

function createBaseline() {
  console.log('📦 Creating bundle size baseline...\n')

  // Build the project
  console.log('Building project...')
  try {
    execSync('npm run build', { stdio: 'inherit' })
  } catch (err) {
    console.error('❌ Build failed')
    process.exit(1)
  }

  const totalSize = getDistSize()
  const chunks = getChunks()

  const baseline = {
    date: new Date().toISOString(),
    totalSize,
    chunks,
    phase: 'baseline'
  }

  fs.writeFileSync(baselineFile, JSON.stringify(baseline, null, 2), 'utf8')

  console.log('\n============================================')
  console.log(`✅ Baseline created`)
  console.log(`Total size: ${formatBytes(totalSize)}`)
  console.log(`Chunks: ${Object.keys(chunks).length}`)
  console.log('============================================\n')

  // Initialize history
  const history = [baseline]
  fs.writeFileSync(historyFile, JSON.stringify(history, null, 2), 'utf8')
}

function checkBundle() {
  console.log('📊 Checking bundle size...\n')

  if (!fs.existsSync(baselineFile)) {
    console.warn('⚠ No baseline found. Creating baseline first...\n')
    createBaseline()
    return
  }

  const baseline = JSON.parse(fs.readFileSync(baselineFile, 'utf8'))
  const currentSize = getDistSize()
  const difference = currentSize - baseline.totalSize
  const percentChange = ((difference / baseline.totalSize) * 100).toFixed(2)

  const current = {
    date: new Date().toISOString(),
    totalSize: currentSize,
    chunks: getChunks(),
    difference,
    percentChange: parseFloat(percentChange)
  }

  // Add to history
  let history = []
  if (fs.existsSync(historyFile)) {
    history = JSON.parse(fs.readFileSync(historyFile, 'utf8'))
  }
  history.push(current)
  fs.writeFileSync(historyFile, JSON.stringify(history, null, 2), 'utf8')

  // Print report
  console.log('============================================')
  console.log('Bundle Size Comparison')
  console.log('============================================')
  console.log(`Baseline:     ${formatBytes(baseline.totalSize)}`)
  console.log(`Current:      ${formatBytes(currentSize)}`)
  console.log(`Change:       ${formatBytes(Math.abs(difference))} (${percentChange}%)`)
  console.log(`Status:       ${percentChange > 0 ? '📈 INCREASE' : '📉 DECREASE'}`)
  console.log('============================================\n')

  // Alert if bundle grows too much
  if (percentChange > 10) {
    console.error(`❌ Bundle size increased by more than 10%!`)
    console.error(`   Consider optimizations or check for unintended changes\n`)
    process.exit(1)
  } else if (percentChange > 5) {
    console.warn(`⚠ Bundle size increased by ${percentChange}%\n`)
  } else if (percentChange < -5) {
    console.log(`✅ Bundle size decreased by ${Math.abs(percentChange)}%!\n`)
  }
}

function showReport() {
  if (!fs.existsSync(historyFile)) {
    console.error('❌ No measurement history found')
    process.exit(1)
  }

  const history = JSON.parse(fs.readFileSync(historyFile, 'utf8'))
  const baseline = history[0]
  const current = history[history.length - 1]

  console.log('\n============================================')
  console.log('Bundle Size Migration Report')
  console.log('============================================\n')

  console.log(`📅 Baseline:      ${new Date(baseline.date).toLocaleDateString()}`)
  console.log(`📅 Last measured: ${new Date(current.date).toLocaleDateString()}\n`)

  console.log(`📦 Baseline size:     ${formatBytes(baseline.totalSize)}`)
  console.log(`📦 Current size:      ${formatBytes(current.totalSize)}`)
  console.log(`📦 Total change:      ${formatBytes(current.totalSize - baseline.totalSize)}`)

  const finalPercent = (((current.totalSize - baseline.totalSize) / baseline.totalSize) * 100).toFixed(2)
  console.log(`📊 Percentage change: ${finalPercent}%\n`)

  console.log('History:')
  history.forEach((entry, i) => {
    const date = new Date(entry.date).toLocaleDateString()
    const size = formatBytes(entry.totalSize)
    const phase = entry.phase || `Phase ${Math.floor(i / 5)}`
    console.log(`  ${date}: ${size} (${phase})`)
  })

  console.log('\n============================================\n')

  if (finalPercent < -5) {
    console.log('✅ Bundle size decreased! Migration successful!\n')
  }
}

// Main execution
console.log('🔨 Bundle Size Comparison Tool\n')

switch (action) {
  case '--baseline':
    createBaseline()
    break

  case '--check':
    checkBundle()
    break

  case '--report':
    showReport()
    break

  default:
    console.log('Usage:')
    console.log('  node scripts/compare-bundle-size.js --baseline  (create baseline)')
    console.log('  node scripts/compare-bundle-size.js --check     (compare with baseline)')
    console.log('  node scripts/compare-bundle-size.js --report    (show migration progress)')
    console.log('')
}
