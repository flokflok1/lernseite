/**
 * User Domain Models
 * ==================
 * Models for user profiles, authentication, sessions
 *
 * GBA (Group-Based Authorization):
 * - UserModel: Full domain model with hierarchy-based role checks
 * - User: Minimal interface for cross-model references (Course.model.ts)
 */

export { UserModel } from './User.model'
export type { User } from './User.types'
