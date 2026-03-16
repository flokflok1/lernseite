/**
 * Vue Router Meta Type Augmentation
 *
 * Extends the RouteMeta interface with custom meta fields
 * used for access control and navigation guards.
 */

import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    /** Requires user to be authenticated */
    requiresAuth?: boolean

    /** Requires user to be a guest (not logged in) */
    requiresGuest?: boolean

    /** Requires user to have Owner role (RBAC 2.0) */
    requiresOwner?: boolean

    /** Requires user to have System Admin role (admin, superadmin) */
    requiresSystemAdmin?: boolean

    /** Requires user to have Organisation Admin role (school_admin, company_admin) */
    requiresOrgAdmin?: boolean

    /** Requires user to have Creator or Teacher role */
    requiresCreatorOrTeacher?: boolean

    /** Route is publicly accessible (no auth required) */
    isPublic?: boolean

    /** Ignore setup wizard check (for setup routes) */
    ignoreSetupCheck?: boolean

    /** Render page without layout wrapper (e.g. popout windows) */
    hideLayout?: boolean
  }
}
