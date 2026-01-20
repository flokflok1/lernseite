/**
 * Feature Flags Store (Deprecated Re-export)
 *
 * @deprecated Import from '@/application/stores/modules/feature-flags' instead
 * This re-export will be REMOVED on 2027-01-20 (12 months)
 * ESLint will error after 2026-07-20 (6 months)
 *
 * Migration Guide:
 * - Old: import { useFeatureFlags } from '@/store/modules/admin/feature-flags.store'
 * - New: import { useFeatureFlags } from '@/application/stores/modules/feature-flags'
 */

export * from '@/application/stores/modules/feature-flags/feature-flags.store'
