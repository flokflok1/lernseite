/**
 * Shared API Types - Barrel Export
 *
 * Central export point for all shared type definitions used across domains.
 * Organized by category for easy discovery and import.
 *
 * Usage:
 * import type {
 *   // Pagination types
 *   PaginatedResponse,
 *   PaginationParams,
 *
 *   // Response types
 *   ApiResponse,
 *   ApiSuccessResponse,
 *   ApiErrorResponse,
 *
 *   // Status types
 *   ModerationStatus,
 *   PriorityLevel,
 *
 *   // Filter types
 *   BaseFilterParams,
 *   ComplexFilterParams,
 *
 *   // Entity types
 *   BaseEntity,
 *   BaseUser,
 *   BaseContent
 * } from '@/infrastructure/api/shared'
 */

// ============================================
// Pagination Types
// ============================================

export type {
  StandardPaginatedResponse,
  PaginatedResponse,
  InfinitePaginatedResponse,
  CursorPaginatedResponse,
  PaginationMetadata,
  PaginationParams,
  SortablePaginationParams,
  DateFilteredPaginationParams,
  SearchablePaginationParams,
} from './pagination'

export {
  calculateOffset,
  calculateTotalPages,
  createPaginatedResponse,
} from './pagination'

// ============================================
// Response Types
// ============================================

export type {
  ApiError,
  ApiMetadata,
  ApiSuccessResponse,
  ApiErrorResponse,
  ApiResponse,
  ApiPaginatedResponse,
  ApiListResponse,
  ApiBulkResponse,
  ApiBulkResult,
  ApiJobResponse,
  ApiJob,
  ApiFileResponse,
  ApiFile,
} from './responses'

export {
  isSuccessResponse,
  isErrorResponse,
  createSuccessResponse,
  createErrorResponse,
} from './responses'

// ============================================
// Status & Priority Types
// ============================================

export type {
  ModerationStatus,
  ReviewStatus,
  AppealStatus,
  ApprovalStatus,
  ProcessingStatus,
  ComplianceStatus,
  ContentStatus,
  UserStatus,
  ActionStatus,
  PriorityLevel,
  ViolationType,
  ModerationDecision,
  AppealDecision,
  RestrictionType,
  RemovalMethod,
  EnforcementActionType,
  ContentType,
  NotificationStatus,
  ConsentStatus,
  FeatureFlagStatus,
} from './statuses'

export {
  isTerminalStatus,
  isValidStatusTransition,
  getStatusLabel,
  getPrioritySeverity,
  comparePriorities,
} from './statuses'

// ============================================
// Filter Types
// ============================================

export type {
  BaseFilterParams,
  StatusFilterParams,
  PriorityFilterParams,
  DateRangeFilterParams,
  RelativeTimeFilterParams,
  CategoryFilterParams,
  SearchableFilterParams,
  OwnershipFilterParams,
  PaginatedSortableStatusFilters,
  PaginatedSortableDateFilters,
  ComplexFilterParams,
  ComplianceAuditFilters,
  ModerationQueueFilters,
} from './filters'

export {
  normalizeFilters,
  hasActiveFilters,
  getActiveFilters,
  filtersToQueryString,
} from './filters'

// ============================================
// Entity Types
// ============================================

export type {
  BaseEntity,
  BaseUser,
  BaseContent,
  BaseAuditEntity,
  TimeRange,
  UserRef,
  ContentRef,
  EngagementMetrics,
  GeoLocation,
  VersionedChange,
  PermissionGrant,
  ValidationError,
  HealthStatus,
} from './entities'

// ============================================
// Re-export all types as a namespace (optional)
// ============================================

import * as PaginationTypes from './pagination'
import * as ResponseTypes from './responses'
import * as StatusTypes from './statuses'
import * as FilterTypes from './filters'
import * as EntityTypes from './entities'

export const SharedTypes = {
  ...PaginationTypes,
  ...ResponseTypes,
  ...StatusTypes,
  ...FilterTypes,
  ...EntityTypes,
}
