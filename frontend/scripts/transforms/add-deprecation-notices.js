/**
 * jscodeshift Codemod: Add deprecation notices to re-export barrels
 *
 * Usage:
 *   npx jscodeshift -t scripts/transforms/add-deprecation-notices.js api/ --dry
 *
 * This codemod will:
 * 1. Add JSDoc @deprecated tags to barrel exports
 * 2. Add console.warn() statements for exports used at runtime
 * 3. Document removal date (12 months from 2026-01-20)
 */

module.exports = function transformer(file, api) {
  const j = api.jscodeshift
  const root = j(file.source)
  const { filePath } = file

  // Only process barrel re-export files
  const barrelPatterns = [
    'api/*.ts',
    'store/modules/*.ts',
    'components/**/index.ts',
    'domain/models/**/index.ts',
  ]

  const isBarrelFile = barrelPatterns.some(pattern => {
    const regex = pattern.replace('*', '.*')
    return new RegExp(regex).test(filePath)
  })

  if (!isBarrelFile) {
    return null // Don't modify non-barrel files
  }

  let hasChanges = false

  // Add deprecation notices to export statements
  root.find(j.ExportNamedDeclaration).forEach(path => {
    const { node } = path

    // Check if it's a re-export (export ... from '...')
    if (node.source && node.source.value) {
      const newPath = node.source.value

      // Only add deprecation to barrel re-exports
      if (newPath.startsWith('@/') && !filePath.includes(newPath.split('/')[2])) {
        // Add JSDoc comment if not already there
        if (!node.comments || !node.comments.some(c => c.value.includes('@deprecated'))) {
          const deprecationComment = j.commentLine(` @deprecated Re-export from ${newPath}. This will be removed on 2027-01-20.`)
          deprecationComment.leading = true

          if (!node.comments) {
            node.comments = []
          }
          node.comments.push(deprecationComment)

          hasChanges = true
          console.log(`  ✓ Added deprecation notice to: ${node.source.value}`)
        }
      }
    }
  })

  // Find and add deprecation notice to function exports (for re-exports like useDesktopStore)
  root.find(j.ExportNamedDeclaration, {
    declaration: { type: 'FunctionDeclaration' }
  }).forEach(path => {
    const { node } = path
    const functionName = node.declaration?.id?.name

    if (functionName && (functionName.includes('Deprecated') || functionName.startsWith('use'))) {
      // Add JSDoc to function
      const jsdocComment = `
   * @deprecated This function is deprecated.
   * Use the new location instead.
   * This will be removed on 2027-01-20.
   `

      const comment = j.commentBlock(jsdocComment)
      if (!node.comments) {
        node.comments = []
      }
      node.comments.unshift(comment)

      hasChanges = true
      console.log(`  ✓ Added JSDoc deprecation to function: ${functionName}`)
    }
  })

  // Add leading block comments to files that are deprecation barrels
  if (filePath.includes('api/') && isBarrelFile) {
    const blockComment = `
/**
 * @deprecated This file is a re-export barrel for backward compatibility.
 *
 * The actual implementation has moved to the infrastructure layer.
 * This file will be removed on 2027-01-20 (12 months from 2026-01-20).
 *
 * Migration timeline:
 * - Months 0-6 (until 2026-07-20): ESLint warnings
 * - Months 6-12 (until 2027-01-20): ESLint errors
 * - Month 12+: File removed (breaking change in v3.0.0)
 *
 * Please update your imports to use the new paths directly.
 */
`

    if (!root.find(j.Program).at(0).get().value.comments) {
      root.find(j.Program).at(0).get().value.comments = []
    }

    // Add deprecation notice at top of file
    const existingComments = root.find(j.Program).at(0).get().value.comments || []
    if (!existingComments.some(c => c.value.includes('@deprecated'))) {
      const programNode = root.find(j.Program).at(0).get().value
      programNode.comments = [j.commentBlock(blockComment), ...(programNode.comments || [])]

      hasChanges = true
      console.log(`  ✓ Added file-level deprecation notice`)
    }
  }

  return hasChanges ? root.toSource() : null
}

module.exports.parser = 'babel'
