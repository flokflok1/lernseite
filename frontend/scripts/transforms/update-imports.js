/**
 * jscodeshift Codemod: Update imports from old DDD locations to new locations
 *
 * Usage:
 *   npx jscodeshift -t scripts/transforms/update-imports.js src/
 *   npx jscodeshift -t scripts/transforms/update-imports.js src/ --dry
 *
 * This codemod will transform imports like:
 *   @/api/courses.api → @/infrastructure/api/clients/content.client
 *   @/store/modules/content → @/application/stores/modules/content
 *   @/components/content → @/presentation/components/content
 */

module.exports = function transformer(file, api) {
  const j = api.jscodeshift
  const root = j(file.source)

  // Mapping of old import paths to new import paths
  const importMappings = {
    // API clients (infrastructure layer)
    '@/api/courses.api': '@/infrastructure/api/clients/content.client',
    '@/api/player.api': '@/infrastructure/api/clients/learning.client',
    '@/api/user.api': '@/infrastructure/api/clients/user.client',
    '@/api/auth.api': '@/infrastructure/api/clients/auth.client',
    '@/api/social.api': '@/infrastructure/api/clients/social.client',
    '@/api/admin.api': '@/infrastructure/api/clients/admin.client',
    '@/api/setup.api': '@/infrastructure/api/clients/setup.client',
    '@/api/examSimulation.api': '@/infrastructure/api/clients/assessment.client',

    // Stores (application layer)
    '@/store/modules/user': '@/application/stores/modules/user',
    '@/store/modules/content': '@/application/stores/modules/content',
    '@/store/modules/learning': '@/application/stores/modules/learning',
    '@/store/modules/social': '@/application/stores/modules/social',
    '@/store/modules/admin': '@/application/stores/modules/admin',
    '@/store/modules/compliance': '@/application/stores/modules/compliance',

    // Components (presentation layer)
    '@/components/content': '@/presentation/components/content',
    '@/components/learning': '@/presentation/components/learning',
    '@/components/user': '@/presentation/components/user',
    '@/components/social': '@/presentation/components/social',
    '@/components/admin': '@/presentation/components/admin',
    '@/components/compliance': '@/presentation/components/compliance',
    '@/components/base': '@/presentation/components/shared/ui',
  }

  let hasChanges = false

  // Find and update import statements
  root.find(j.ImportDeclaration).forEach(path => {
    const importPath = path.node.source.value

    // Check if this import path should be transformed
    Object.entries(importMappings).forEach(([oldPath, newPath]) => {
      if (importPath === oldPath) {
        path.node.source.value = newPath
        hasChanges = true
        console.log(`  ✓ ${oldPath} → ${newPath}`)
      }
    })
  })

  // Find and update require statements (for CommonJS)
  root.find(j.CallExpression, {
    callee: { name: 'require' }
  }).forEach(path => {
    const requirePath = path.node.arguments[0]?.value

    if (typeof requirePath === 'string') {
      Object.entries(importMappings).forEach(([oldPath, newPath]) => {
        if (requirePath === oldPath) {
          path.node.arguments[0].value = newPath
          hasChanges = true
          console.log(`  ✓ require('${oldPath}') → require('${newPath}')`)
        }
      })
    }
  })

  // Find and update dynamic imports
  root.find(j.CallExpression, {
    callee: { name: 'import' }
  }).forEach(path => {
    const importPath = path.node.arguments[0]?.value

    if (typeof importPath === 'string') {
      Object.entries(importMappings).forEach(([oldPath, newPath]) => {
        if (importPath === oldPath) {
          path.node.arguments[0].value = newPath
          hasChanges = true
          console.log(`  ✓ import('${oldPath}') → import('${newPath}')`)
        }
      })
    }
  })

  return hasChanges ? root.toSource() : null
}

module.exports.parser = 'babel'
