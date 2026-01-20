/**
 * @deprecated Import from '@/api/social' instead
 *
 * This file provides backward compatibility for imports during the DDD migration.
 * All feedback APIs have been moved to the Social Domain.
 *
 * Old way (deprecated):
 * import { submitFeedback, getMyFeedback } from '@/api/feedback.api'
 *
 * New way (preferred):
 * import { submitFeedback, getMyFeedback } from '@/api/social'
 *
 * This re-export will be removed on 2027-01-20 (12 months from 2026-01-20).
 * ESLint will report errors after 2026-07-20 (6 months from now).
 *
 * @see {@link /api/social} for the new location
 */

export * from './social/feedback.api'
export type * from './social/types'
