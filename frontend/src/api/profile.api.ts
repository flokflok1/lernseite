/**
 * @deprecated Import from '@/api/user' instead
 *
 * This file provides backward compatibility for imports during the DDD migration.
 * All profile and preference APIs have been moved to the User Domain.
 *
 * Old way (deprecated):
 * import { getProfile, updateProfile } from '@/api/profile.api'
 *
 * New way (preferred):
 * import { getProfile, updateProfile } from '@/api/user'
 *
 * This re-export will be removed on 2027-01-20 (12 months from 2026-01-20).
 * ESLint will report errors after 2026-07-20 (6 months from now).
 *
 * @see {@link /api/user} for the new location
 */

export * from './user/profile.api'
export type * from './user/types'
