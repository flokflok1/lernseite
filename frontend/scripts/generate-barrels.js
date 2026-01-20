#!/usr/bin/env node

/**
 * Generate Barrel Exports for Backward Compatibility
 *
 * This script automatically generates index.ts files that re-export from new locations
 * to maintain backward compatibility during the DDD migration.
 *
 * Usage:
 *   node scripts/generate-barrels.js
 *   node scripts/generate-barrels.js --domain content  (specific domain)
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const args = process.argv.slice(2)
const domainFilter = args.includes('--domain')
  ? args[args.indexOf('--domain') + 1]
  : null

// Mapping of old location → new location for barrel generation
const barrelMappings = [
  {
    oldPath: 'src/api',
    newPath: 'src/infrastructure/api/clients',
    filePattern: '*.api.ts',
    transform: (filename) => filename.replace('.api.ts', '.client.ts'),
    description: 'API Clients'
  },
  {
    oldPath: 'src/components',
    newPath: 'src/presentation/components',
    filePattern: '[a-z]*/index.ts',
    subdirs: true,
    description: 'Components'
  },
  {
    oldPath: 'src/store/modules',
    newPath: 'src/application/stores/modules',
    filePattern: '[a-z]*/index.ts',
    subdirs: true,
    description: 'Stores'
  }
]

const DEPRECATION_TEMPLATE = (newPath) => `
/**
 * @deprecated This is a re-export barrel for backward compatibility.
 *
 * Import directly from the new location instead:
 *   @/${newPath}
 *
 * This file will be REMOVED on 2027-01-20 (12 months from 2026-01-20).
 *
 * Migration timeline:
 * - Months 0-6 (until 2026-07-20): ESLint warnings on old imports
 * - Months 6-12 (until 2027-01-20): ESLint errors on old imports
 * - Month 12+: This file removed (breaking change in v3.0.0)
 */

export * from '@/${newPath}'
`

function generateBarrelForFile(oldPath, newPath, filename) {
  const barrelPath = path.join(oldPath, filename)
  const relativeNewPath = newPath.replace('src/', '')

  // Create parent directory if needed
  const dir = path.dirname(barrelPath)
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true })
  }

  // Check if barrel already exists
  if (fs.existsSync(barrelPath)) {
    const content = fs.readFileSync(barrelPath, 'utf8')
    if (content.includes('@deprecated')) {
      return false // Already a deprecation barrel
    }
  }

  // Generate barrel content
  const content = DEPRECATION_TEMPLATE(relativeNewPath)

  fs.writeFileSync(barrelPath, content.trim() + '\n', 'utf8')
  return true
}

function generateBarrelsForDirectory(oldPath, newPath, filePattern) {
  if (!fs.existsSync(newPath)) {
    console.warn(`  ⚠ New location not found: ${newPath}`)
    return 0
  }

  let count = 0

  // List directories in new location
  const dirs = fs.readdirSync(newPath).filter(file => {
    const fullPath = path.join(newPath, file)
    return fs.statSync(fullPath).isDirectory()
  })

  dirs.forEach(dir => {
    // Check if this domain should be processed
    if (domainFilter && !dir.includes(domainFilter)) {
      return
    }

    // Check if domain exists in old location (if so, it needs a barrel)
    const oldDomainPath = path.join(oldPath, dir)
    if (!fs.existsSync(oldDomainPath) || !fs.statSync(oldDomainPath).isDirectory()) {
      // Create barrel for this domain
      const barrelPath = path.join(oldPath, dir, 'index.ts')
      if (generateBarrelForFile(path.dirname(barrelPath), path.join(newPath, dir), 'index.ts')) {
        console.log(`    ✓ Generated barrel: ${barrelPath}`)
        count++
      }
    }
  })

  return count
}

// Main execution
console.log('🚀 Generating backward-compatible barrel exports...\n')

let totalGenerated = 0

barrelMappings.forEach(mapping => {
  if (domainFilter && !mapping.description.toLowerCase().includes(domainFilter)) {
    return
  }

  console.log(`📦 ${mapping.description}`)

  if (mapping.subdirs) {
    const generated = generateBarrelsForDirectory(mapping.oldPath, mapping.newPath)
    totalGenerated += generated
  } else {
    // Handle flat file mappings (like API files)
    if (!fs.existsSync(mapping.newPath)) {
      console.warn(`  ⚠ New location not found: ${mapping.newPath}`)
      return
    }

    const files = fs.readdirSync(mapping.newPath).filter(f => f.endsWith('.client.ts'))

    files.forEach(file => {
      const oldFileName = file.replace('.client.ts', '.api.ts')
      const oldPath = path.join(mapping.oldPath, oldFileName)

      if (generateBarrelForFile(mapping.oldPath, path.join(mapping.newPath, file), oldFileName)) {
        console.log(`    ✓ Generated barrel: ${oldPath}`)
        totalGenerated++
      }
    })
  }

  console.log('')
})

console.log('============================================')
console.log(`✅ Generated ${totalGenerated} barrel exports`)
console.log('============================================')
console.log('')
console.log('Next steps:')
console.log('  1. Review generated files: git diff')
console.log('  2. Run validation: npm run validate:imports')
console.log('  3. Commit: git add -A && git commit -m "refactor(ddd): generate backward-compatible barrels"')
console.log('')
