/**
 * Shared Base Entity Types
 *
 * Standardized base entity interfaces used across all API domains.
 * Provides common fields and patterns for domain entities.
 *
 * Usage:
 * import type {
 *   BaseEntity,
 *   BaseUser,
 *   BaseContent,
 *   BaseAuditEntity,
 *   TimeRange
 * } from '@/api/shared'
 */

/**
 * Base entity with minimal required fields.
 *
 * All domain entities should extend this interface.
 *
 * @example
 * interface Post extends BaseEntity {
 *   title: string
 *   content: string
 * }
 */
export interface BaseEntity {
  /** Unique identifier */
  id: string

  /** When entity was created (ISO 8601 format) */
  created_at: string

  /** When entity was last updated (ISO 8601 format) */
  updated_at?: string
}

/**
 * Base user entity with common user fields.
 *
 * Extended by user-specific types in user domain.
 *
 * @example
 * interface AdminUser extends BaseUser {
 *   permissions: string[]
 * }
 */
export interface BaseUser extends BaseEntity {
  /** User's email address */
  email: string

  /** User's display name */
  name: string

  /** User's role (student, teacher, admin, etc.) */
  role: string

  /** Whether user account is active */
  is_active: boolean

  /** When user last logged in */
  last_login?: string
}

/**
 * Base content entity with common content fields.
 *
 * Extended by content-specific types (posts, courses, lessons, etc.).
 *
 * @example
 * interface Post extends BaseContent {
 *   content: string
 *   likes_count: number
 * }
 */
export interface BaseContent extends BaseEntity {
  /** Content title or heading */
  title: string

  /** Content description or summary */
  description?: string

  /** Type of content (post, course, lesson, etc.) */
  type: string

  /** Status of content (draft, published, archived, etc.) */
  status: string

  /** User who created this content */
  created_by: string

  /** Whether content is visible/available */
  is_active: boolean

  /** Optional metadata key-value pairs */
  metadata?: Record<string, any>
}

/**
 * Base audit entity with audit trail fields.
 *
 * Used for entities that require change tracking.
 *
 * @example
 * interface AuditLog extends BaseAuditEntity {
 *   action: string
 *   changes: Record<string, any>
 * }
 */
export interface BaseAuditEntity extends BaseEntity {
  /** User ID who created the entity */
  created_by: string

  /** User ID who last updated the entity */
  updated_by?: string

  /** Reason for the last update */
  change_reason?: string

  /** Version number (incremented on each update) */
  version: number

  /** Whether entity has been soft-deleted */
  is_deleted: boolean

  /** When entity was deleted (if soft-deleted) */
  deleted_at?: string

  /** User who deleted the entity */
  deleted_by?: string
}

/**
 * Time range for filtering by date.
 *
 * Used in analytics, reporting, and audit queries.
 *
 * @example
 * const range: TimeRange = {
 *   from_date: '2026-01-01',
 *   to_date: '2026-01-31'
 * }
 */
export interface TimeRange {
  /** Start date (ISO 8601 format, inclusive) */
  from_date: string

  /** End date (ISO 8601 format, inclusive) */
  to_date: string

  /** Optional timezone for date calculations */
  timezone?: string
}

/**
 * Minimal user reference for embedding in other entities.
 *
 * Used when including creator/author info in responses.
 *
 * @example
 * interface Post {
 *   id: string
 *   title: string
 *   author: UserRef
 * }
 */
export interface UserRef {
  /** User ID */
  id: string

  /** User's display name */
  name: string

  /** User's avatar URL (if available) */
  avatar_url?: string
}

/**
 * Minimal content reference for embedding in other entities.
 *
 * Used when referencing related content items.
 *
 * @example
 * interface Comment {
 *   id: string
 *   content: Post extends { id, title }
 *   post: ContentRef
 * }
 */
export interface ContentRef {
  /** Content ID */
  id: string

  /** Content title */
  title: string

  /** Content type (post, course, lesson, etc.) */
  type: string

  /** Content status (draft, published, etc.) */
  status?: string
}

/**
 * Engagement metrics for content.
 *
 * Summarizes user interaction with content.
 *
 * @example
 * interface Post {
 *   id: string
 *   title: string
 *   metrics: EngagementMetrics
 * }
 */
export interface EngagementMetrics {
  /** Number of views/impressions */
  views: number

  /** Number of likes/reactions */
  likes: number

  /** Number of comments/replies */
  comments: number

  /** Number of shares */
  shares: number

  /** Number of saves/bookmarks */
  saves: number

  /** Engagement rate (0-1) */
  engagement_rate: number
}

/**
 * Location/geography information.
 *
 * Used for location-based features and analytics.
 *
 * @example
 * interface User {
 *   id: string
 *   name: string
 *   location: GeoLocation
 * }
 */
export interface GeoLocation {
  /** Country code (ISO 3166-1 alpha-2) */
  country_code: string

  /** Region/state code */
  region_code?: string

  /** City name */
  city?: string

  /** Latitude coordinate */
  latitude?: number

  /** Longitude coordinate */
  longitude?: number

  /** Timezone (IANA format, e.g., Europe/Berlin) */
  timezone?: string
}

/**
 * Versioned change tracking for audit trail.
 *
 * Records what changed, who changed it, and when.
 *
 * @example
 * interface ChangeLog {
 *   entity_id: string
 *   changes: VersionedChange[]
 * }
 */
export interface VersionedChange {
  /** Version number after this change */
  version: number

  /** Who made the change (user ID) */
  changed_by: string

  /** When the change was made */
  changed_at: string

  /** Field name that was changed */
  field_name: string

  /** Previous value before this change */
  old_value?: any

  /** New value after this change */
  new_value?: any

  /** Reason or description of the change */
  change_reason?: string
}

/**
 * Permission/capability grant.
 *
 * Represents a single permission or capability granted to a user.
 *
 * @example
 * interface User {
 *   id: string
 *   permissions: PermissionGrant[]
 * }
 */
export interface PermissionGrant {
  /** Permission code/identifier */
  permission: string

  /** Resource this permission applies to (user, post, course, etc.) */
  resource_type?: string

  /** Specific resource ID (if applicable) */
  resource_id?: string

  /** When permission was granted */
  granted_at: string

  /** When permission expires (optional) */
  expires_at?: string

  /** Whether permission is currently active */
  is_active: boolean

  /** Reason permission was granted */
  grant_reason?: string
}

/**
 * Validation error detail.
 *
 * Represents a single validation error with field and reason.
 *
 * @example
 * interface ValidationResult {
 *   valid: false
 *   errors: ValidationError[]
 * }
 */
export interface ValidationError {
  /** Field name that failed validation */
  field: string

  /** Error code (required, invalid_format, etc.) */
  code: string

  /** Human-readable error message */
  message: string

  /** Actual value that failed validation */
  value?: any

  /** Constraint that was violated (e.g., "min_length: 3") */
  constraint?: string
}

/**
 * Health check response for service status.
 *
 * Used by health check endpoints to report service status.
 *
 * @example
 * const health: HealthStatus = {
 *   status: 'healthy',
 *   checks: {
 *     database: 'ok',
 *     cache: 'ok'
 *   }
 * }
 */
export interface HealthStatus {
  /** Overall status (healthy, degraded, unhealthy) */
  status: 'healthy' | 'degraded' | 'unhealthy'

  /** Individual component health checks */
  checks: Record<string, string>

  /** Timestamp of health check */
  timestamp: string

  /** Service version */
  version?: string

  /** Additional diagnostic information */
  diagnostics?: Record<string, any>
}
