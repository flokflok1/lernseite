/**
 * User Domain Types
 *
 * Canonical type definitions for user-related domain concepts.
 * Infrastructure layer re-exports these for API response typing.
 */

/**
 * Group information for Group-Based Authorization (GBA).
 * Determines user access tier via hierarchy_level.
 */
export interface UserGroup {
  id: string
  name: string
  slug: string
  type: string
  hierarchy_level: number
  access_level: string
}
