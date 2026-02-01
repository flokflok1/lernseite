/**
 * User Type Definitions
 *
 * Simple types for user references in domain models.
 * No hardcoded roles - all permissions come from database.
 */

/**
 * Minimal User interface for domain model usage
 */
export interface User {
  id: string
  isSystemAdmin: boolean
}
