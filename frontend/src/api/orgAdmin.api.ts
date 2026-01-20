/**
 * @deprecated Import from '@/api/admin' instead
 *
 * This file provides backward compatibility for imports during the DDD migration.
 * All organisation administration APIs have been moved to the Admin Domain.
 *
 * Old way (deprecated):
 * import { getOrganisationDetail, getOrganisationMembers } from '@/api/orgAdmin.api'
 *
 * New way (preferred):
 * import { getOrganisationDetail, getOrganisationMembers } from '@/api/admin'
 *
 * This re-export will be removed on 2027-01-20 (12 months from 2026-01-20).
 * ESLint will report errors after 2026-07-20 (6 months from now).
 *
 * @see {@link /api/admin} for the new location
 */

export * from './admin/organisations/management.api'
export * from './admin/organisations/courses.api'
export * from './admin/organisations/analytics.api'
export type * from './admin/organisations/types'
