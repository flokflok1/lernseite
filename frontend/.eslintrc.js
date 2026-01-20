/**
 * ESLint Configuration - Frontend DDD Migration
 *
 * This configuration enforces the Domain-Driven Design (DDD) migration
 * with a deprecation strategy:
 *
 * Timeline:
 * - 2026-01-20 to 2026-07-20 (Months 0-6): Warn about deprecated imports
 * - 2026-07-20 to 2027-01-20 (Months 6-12): Error on deprecated imports
 * - 2027-01-20+: Deprecated imports removed (breaking change v3.0.0)
 *
 * Deprecation Pattern:
 * - Re-export barrels remain at old locations with @deprecated JSDoc
 * - Developers warned to migrate to new locations
 * - All old paths will break in v3.0.0
 */

module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true
  },
  extends: [
    'plugin:vue/vue3-recommended',
    'eslint:recommended',
    '@vue/eslint-config-typescript'
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  rules: {
    // ============================================
    // DDD MIGRATION DEPRECATION RULES (2026-01-20)
    // ============================================

    'no-restricted-imports': [
      'warn', // Change to 'error' after 2026-07-20
      {
        patterns: [
          // ========== API Clients ==========
          {
            group: ['@/api/*'],
            message: [
              '❌ DEPRECATED: Old API path @/api/* is deprecated.',
              'ℹ️  Migrate to: @/infrastructure/api/clients/{domain}.client',
              '📅 Timeline: Warnings until 2026-07-20, Errors until 2027-01-20',
              '📚 See: .claude/FRONTEND_DDD_MIGRATION_PLAN.md'
            ].join('\n')
          },

          // ========== Components ==========
          {
            group: ['@/components/base/*'],
            message: [
              '❌ DEPRECATED: Old components/base/* path is deprecated.',
              'ℹ️  Migrate to: @/presentation/components/shared/ui/{Component}',
              '📅 Timeline: Warnings until 2026-07-20, Errors until 2027-01-20',
              '📚 See: .claude/FRONTEND_DDD_MIGRATION_PLAN.md'
            ].join('\n')
          },
          {
            group: ['@/components/admin/*'],
            message: [
              '❌ DEPRECATED: Old components/admin/* path is deprecated.',
              'ℹ️  Migrate to: @/presentation/components/admin/{Feature}',
              '📅 Timeline: Warnings until 2026-07-20, Errors until 2027-01-20'
            ].join('\n')
          },
          {
            group: ['@/components/user/*'],
            message: [
              '❌ DEPRECATED: Old components/user/* path is deprecated.',
              'ℹ️  Migrate to: @/presentation/components/user/{Feature}',
              '📅 Timeline: Warnings until 2026-07-20, Errors until 2027-01-20'
            ].join('\n')
          },

          // ========== Stores ==========
          {
            group: ['@/store/modules/*'],
            message: [
              '❌ DEPRECATED: Old store/modules/* path is deprecated.',
              'ℹ️  Migrate to: @/application/stores/modules/{domain}',
              '📅 Timeline: Warnings until 2026-07-20, Errors until 2027-01-20',
              '⚠️  Special: useDesktopStore → useWorkspaceStore (facade migration)'
            ].join('\n')
          },

          // ========== Domain Models (Old Paths) ==========
          {
            group: ['@/domain/models/course/*'],
            message: [
              '❌ DEPRECATED: Old domain/models/course/* path is deprecated.',
              'ℹ️  Migrate to: @/domain/models/content/course',
              '📅 Timeline: Warnings until 2026-07-20, Errors until 2027-01-20'
            ].join('\n')
          },
          {
            group: ['@/domain/models/post/*'],
            message: [
              '❌ DEPRECATED: Old domain/models/post/* path is deprecated.',
              'ℹ️  Migrate to: @/domain/models/social/post',
              '📅 Timeline: Warnings until 2026-07-20, Errors until 2027-01-20'
            ].join('\n')
          }
        ]
      }
    ],

    // ========== Vue Rules ==========
    'vue/multi-word-component-names': 'error',
    'vue/component-name-in-template-casing': ['error', 'PascalCase'],
    'vue/no-v-html': 'warn',
    'vue/require-default-prop': 'error',
    'vue/require-prop-types': 'error',
    'vue/no-unused-vars': 'error',
    'vue/no-unused-components': 'warn',

    // ========== Code Quality ==========
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
    'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    'prefer-const': 'error',
    'no-var': 'error',
    'eqeqeq': ['error', 'always'],
    'no-implicit-coercion': 'error',

    // ========== Complexity ==========
    'complexity': ['warn', 10],
    'max-depth': ['warn', 4],
    'max-lines': ['warn', { max: 500, skipBlankLines: true }],
    'max-lines-per-function': ['warn', { max: 100, skipBlankLines: true }],
    'max-nested-callbacks': ['warn', 3]
  },
  overrides: [
    {
      files: ['*.vue'],
      rules: {
        'max-lines': ['warn', { max: 500, skipBlankLines: true }]
      }
    },
    {
      files: ['*.ts', '*.tsx'],
      parser: '@typescript-eslint/parser',
      extends: ['plugin:@typescript-eslint/recommended'],
      rules: {
        '@typescript-eslint/no-explicit-any': 'warn',
        '@typescript-eslint/explicit-function-return-types': 'off',
        '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }]
      }
    }
  ],

  // ========== Documentation ==========
  /**
   * DDD MIGRATION RULES MAPPING
   *
   * Old Path                          → New Path
   * ==========================================
   * @/api/courses.api.ts             → @/infrastructure/api/clients/content.client.ts
   * @/api/player.api.ts              → @/infrastructure/api/clients/learning.client.ts
   * @/api/[domain].api.ts            → @/infrastructure/api/clients/[domain].client.ts
   *
   * @/components/base/*              → @/presentation/components/shared/ui/*
   * @/components/[domain]/*          → @/presentation/components/[domain]/*
   *
   * @/store/modules/[domain]/*       → @/application/stores/modules/[domain]/*
   *
   * @/domain/models/course/*         → @/domain/models/content/course/*
   * @/domain/models/post/*           → @/domain/models/social/post/*
   *
   * MORE INFORMATION:
   * - Plan: .claude/FRONTEND_DDD_MIGRATION_PLAN.md
   * - Phase 0 Status: See TodoList in session context
   * - Issue Tracker: GitHub/Issues (tagged ddd-migration)
   */
};
