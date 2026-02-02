#!/usr/bin/env node

/**
 * Frontend DDD Migration Script
 *
 * Reorganizes src/ to match DDD v4.0.2 structure:
 * - presentation/ (UI layer)
 * - application/ (Business logic)
 * - domain/ (Models)
 * - infrastructure/ (APIs, External services)
 * - shared/ (Cross-cutting)
 *
 * Usage: node scripts/migrate-to-ddd.js [--dry-run] [--phase 1-8]
 */

import fs from 'fs'
import path from 'path'
import { execSync } from 'child_process'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const rootDir = path.join(__dirname, '..')
const srcDir = path.join(rootDir, 'src')

const args = process.argv.slice(2)
const isDryRun = args.includes('--dry-run')
const phase = args.find(arg => arg.startsWith('--phase'))?.split(' ')[1] || 'all'

console.log('🚀 Frontend DDD Migration Script')
console.log(`📋 Dry Run: ${isDryRun ? 'YES' : 'NO'}`)
console.log(`🎯 Phase: ${phase}`)
console.log('')

// Migration mappings
const migrations = {
  presentation: {
    components: [
      { from: 'src/components/admin', to: 'src/presentation/components/admin' },
      { from: 'src/components/compliance', to: 'src/presentation/components/compliance' },
      { from: 'src/components/social', to: 'src/presentation/components/social' },
      { from: 'src/components/security', to: 'src/presentation/components/security' },
      { from: 'src/components/moderation', to: 'src/presentation/components/moderation' },
      { from: 'src/components/feature-flags', to: 'src/presentation/components/admin/feature-flags' },
      { from: 'src/components/base', to: 'src/presentation/components/shared/ui' },
      { from: 'src/components/studio', to: 'src/presentation/components/course-editor' },
    ],
    views: [
      { from: 'src/pages/admin', to: 'src/presentation/views/admin' },
      { from: 'src/pages/auth', to: 'src/presentation/views/auth' },
      { from: 'src/pages/courses', to: 'src/presentation/views/content' },
      { from: 'src/pages/dashboard', to: 'src/presentation/views/dashboard' },
      { from: 'src/pages/social', to: 'src/presentation/views/social' },
      { from: 'src/pages/creator', to: 'src/presentation/views/course-editor' },
      { from: 'src/pages/moderation', to: 'src/presentation/views/moderation' },
    ],
    router: [
      { from: 'src/router', to: 'src/presentation/router' },
    ]
  },

  application: {
    stores: [
      { from: 'src/store/modules', to: 'src/application/stores/modules' },
    ]
  },

  domain: {
    models: [
      { from: 'src/domain/models', to: 'src/domain/models' }, // Keep but reorganize internally
      { from: 'src/domain/value-objects', to: 'src/domain/value-objects' },
    ]
  },

  infrastructure: {
    api: [
      { from: 'src/api', to: 'src/infrastructure/api/clients' },
    ]
  }
}

function moveDir(from, to) {
  const fullFrom = path.join(rootDir, from)
  const fullTo = path.join(rootDir, to)

  if (!fs.existsSync(fullFrom)) {
    console.warn(`  ⚠️  Source not found: ${from}`)
    return false
  }

  console.log(`  ${isDryRun ? '📋' : '📦'} ${from} → ${to}`)

  if (!isDryRun) {
    // Create parent directory if needed
    const parentDir = path.dirname(fullTo)
    if (!fs.existsSync(parentDir)) {
      fs.mkdirSync(parentDir, { recursive: true })
    }

    // Move directory
    if (fs.existsSync(fullTo)) {
      console.warn(`    ⚠️  Target already exists: ${to}`)
      return false
    }

    try {
      execSync(`mv "${fullFrom}" "${fullTo}"`, { stdio: 'ignore' })
      return true
    } catch (e) {
      console.error(`    ❌ Failed to move: ${e.message}`)
      return false
    }
  }

  return true
}

function executePhase(phaseName, phaseConfig) {
  console.log(`\n${'='.repeat(50)}`)
  console.log(`📍 Phase: ${phaseName.toUpperCase()}`)
  console.log(`${'='.repeat(50)}\n`)

  let count = 0

  for (const [category, items] of Object.entries(phaseConfig)) {
    console.log(`\n📂 ${category.toUpperCase()}`)

    for (const item of items) {
      if (moveDir(item.from, item.to)) {
        count++
      }
    }
  }

  console.log(`\n✅ Phase ${phaseName}: ${count} directories processed`)
  return count
}

// Execute migration
try {
  let totalMoved = 0

  if (phase === 'all' || phase === '1') {
    totalMoved += executePhase('presentation', migrations.presentation)
  }

  if (phase === 'all' || phase === '2') {
    totalMoved += executePhase('application', migrations.application)
  }

  if (phase === 'all' || phase === '3') {
    totalMoved += executePhase('domain', migrations.domain)
  }

  if (phase === 'all' || phase === '4') {
    totalMoved += executePhase('infrastructure', migrations.infrastructure)
  }

  console.log(`\n${'='.repeat(50)}`)
  console.log(`✅ Migration Complete!`)
  console.log(`${'='.repeat(50)}`)
  console.log(`📊 Total directories moved: ${totalMoved}`)
  console.log(`${isDryRun ? '📋 Dry run completed - no files were moved' : '✨ All files reorganized!'}`)
  console.log('')
  console.log('Next steps:')
  console.log('  1. npm run validate:imports')
  console.log('  2. npm run typecheck')
  console.log('  3. npm run test')
  console.log('  4. npm run build')

} catch (error) {
  console.error('❌ Migration failed:', error.message)
  process.exit(1)
}
