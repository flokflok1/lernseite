#!/usr/bin/env node

/**
 * Validate Imports - Check for broken imports in the codebase
 *
 * This script scans all TypeScript/Vue files and validates that all imports
 * can be resolved correctly. Used to catch broken imports during DDD migration.
 *
 * Usage:
 *   node scripts/validate-imports.js
 *   node scripts/validate-imports.js --fix  (auto-fix some issues)
 */

import fs from 'fs'
import path from 'path'
import ts from 'typescript'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const args = process.argv.slice(2)
const shouldFix = args.includes('--fix')

// Path aliases (matching tsconfig.json)
const pathAliases = {
  '@': path.resolve(__dirname, '../src')
}

let errors = []
let warnings = []

function resolvePath(importPath) {
  // Handle path aliases
  let resolvedPath = importPath
  Object.entries(pathAliases).forEach(([alias, basePath]) => {
    if (importPath.startsWith(alias + '/')) {
      resolvedPath = importPath.replace(alias, basePath)
    }
  })

  // Check if the import path already has a file extension (including assets)
  const hasExtension = /\.(ts|tsx|vue|js|jsx|svg|png|jpg|jpeg|gif|webp|json|css|scss|less)$/.test(resolvedPath)

  if (hasExtension) {
    // If it already has an extension, check if it exists directly
    if (fs.existsSync(resolvedPath)) {
      return resolvedPath
    }
    return null
  }

  // Try different extensions (for imports without extensions)
  const extensions = ['.ts', '.tsx', '.vue', '.js', '.jsx', '/index.ts', '/index.tsx', '/index.vue', '/index.js']

  for (const ext of extensions) {
    const fullPath = resolvedPath + (ext.startsWith('/') ? '' : '') + ext
    if (fs.existsSync(fullPath)) {
      return fullPath
    }
  }

  return null
}

function validateFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8')

    // Find all import/require statements
    const importRegex = /(?:import\s+.*\s+from\s+['"]([^'"]+)['"]|require\s*\(\s*['"]([^'"]+)['"]\s*\))/g
    let match

    while ((match = importRegex.exec(content)) !== null) {
      const importPath = match[1] || match[2]

      // Skip node_modules and relative imports that exist
      if (!importPath.startsWith('@/') && !importPath.startsWith('#/')) {
        continue
      }

      // Check if path can be resolved
      const resolved = resolvePath(importPath)

      if (!resolved) {
        const lineNum = content.substring(0, match.index).split('\n').length
        errors.push({
          file: filePath,
          line: lineNum,
          import: importPath,
          message: `Cannot resolve import: ${importPath}`
        })
      }
    }
  } catch (err) {
    warnings.push({
      file: filePath,
      message: `Error reading file: ${err.message}`
    })
  }
}

function scanDirectory(dir) {
  const files = fs.readdirSync(dir)

  files.forEach(file => {
    const fullPath = path.join(dir, file)
    const stat = fs.statSync(fullPath)

    // Skip node_modules and hidden directories
    if (file === 'node_modules' || file.startsWith('.') || file === 'dist') {
      return
    }

    if (stat.isDirectory()) {
      scanDirectory(fullPath)
    } else if (file.endsWith('.ts') || file.endsWith('.tsx') || file.endsWith('.vue')) {
      validateFile(fullPath)
    }
  })
}

// Main execution
console.log('🔍 Validating imports...\n')

const srcPath = path.resolve(__dirname, '../src')
scanDirectory(srcPath)

// Print results
console.log('============================================')

if (errors.length === 0 && warnings.length === 0) {
  console.log('✅ All imports are valid!')
  process.exit(0)
}

if (errors.length > 0) {
  console.error(`\n❌ Found ${errors.length} broken imports:\n`)

  errors.slice(0, 20).forEach(err => {
    console.error(`  ${err.file}:${err.line}`)
    console.error(`    ⚠ ${err.message}`)
    console.error(`    import: ${err.import}`)
    console.error('')
  })

  if (errors.length > 20) {
    console.error(`  ... and ${errors.length - 20} more`)
  }

  process.exit(1)
}

if (warnings.length > 0) {
  console.warn(`\n⚠ ${warnings.length} warnings:\n`)

  warnings.slice(0, 10).forEach(w => {
    console.warn(`  ${w.file}: ${w.message}`)
  })

  if (warnings.length > 10) {
    console.warn(`  ... and ${warnings.length - 10} more`)
  }
}

console.log('============================================\n')
