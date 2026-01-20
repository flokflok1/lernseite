/**
 * Shared Utilities Barrel Export
 *
 * Centralized export of all utility functions across domains.
 * Provides type-safe, reusable utilities for validation, formatting,
 * error handling, time operations, pagination, and response adaptation.
 *
 * Usage:
 * import {
 *   // Validators
 *   isEmail,
 *   isValidDate,
 *   isValidStatus,
 *   // Formatters
 *   formatDate,
 *   formatCurrency,
 *   // Error handling
 *   parseApiError,
 *   getErrorMessage,
 *   // Time utilities
 *   formatDuration,
 *   calculateSLADeadline,
 *   // Pagination
 *   calculateTotalPages,
 *   getScrollProgress,
 *   // Adapters
 *   adaptPaginatedResponse,
 *   normalizeCollection
 * } from '@/api/shared/utils'
 */

// ============================================
// Validators
// ============================================

export {
  // Email & URL
  isEmail,
  isUrl,
  isAbsoluteUrl,
  // Date
  isValidDate,
  isPastDate,
  isFutureDate,
  isDateInRange,
  // String
  isNonEmpty,
  isLengthInRange,
  isAlphanumeric,
  isSlug,
  isKebabCase,
  // Number
  isPositiveInteger,
  isNonNegativeInteger,
  isNumberInRange,
  isPercentage,
  // Enum & Status
  isEnumValue,
  isValidStatus,
  isPriority,
  // Array
  isNonEmptyArray,
  isArrayLengthInRange,
  isArrayUnique,
  // Object
  isObject,
  isObjectWithKeys,
  isObjectWithStringValues
} from './validators'

// ============================================
// Formatters
// ============================================

export {
  // Date & Time
  formatDate,
  formatDateTime,
  formatShortDate,
  formatTime,
  formatRelativeTime,
  // Numbers
  formatNumber,
  formatPercentage,
  formatCurrency,
  // Bytes
  formatBytes,
  // Text
  capitalize,
  toTitleCase,
  camelToTitle,
  truncate,
  slugify,
  formatPhone,
  highlightText,
  escapeHtml
} from './formatters'

// ============================================
// Error Handling
// ============================================

export {
  // Type guards
  isApiError,
  isApiErrorResponse,
  isHttpError,
  isValidationError,
  // Parsing
  parseApiError,
  getErrorMessage,
  getErrorDescription,
  getValidationErrorFields,
  getFieldError,
  // Creation
  createApiError,
  createHttpError,
  createValidationError,
  // HTTP Status
  getStatusCategory,
  isSuccessStatus,
  isClientError,
  isServerError,
  isRetryableError,
  // Logging
  logError
} from './errors'

// ============================================
// Time Utilities
// ============================================

export {
  // Date manipulation
  addDays,
  addHours,
  addMinutes,
  addMonths,
  addYears,
  // Period start/end
  getStartOfDay,
  getEndOfDay,
  getStartOfWeek,
  getEndOfWeek,
  getStartOfMonth,
  getEndOfMonth,
  // Date ranges
  getDateRange,
  // Duration
  getDuration,
  getDurationBreakdown,
  formatDuration,
  // SLA
  calculateSLADeadline,
  isDeadlineOverdue,
  getTimeRemaining,
  formatTimeRemaining,
  // Date checks
  isToday,
  isSameDay,
  // Constants
  TIME_UNITS
} from './time'

// ============================================
// Pagination Utilities
// ============================================

export {
  // Calculations
  getNextPageParams,
  getPreviousPageParams,
  calculateTotalPages,
  calculatePageBoundaries,
  getPageRangeText,
  // Cursor-based
  getCursorFromItem,
  decodeCursor,
  isPaginationComplete,
  // Infinite Scroll
  shouldFetchMore,
  getScrollProgress,
  isAtScrollEnd,
  getDistanceFromBottom,
  // Batch Processing
  batchArray,
  processBatchesAsync,
  // State Management
  createPaginationState,
  updatePaginationState,
  resetPaginationState,
  goToPage,
  nextPage,
  previousPage,
  type PaginationState
} from './pagination'

// ============================================
// Response Adapters
// ============================================

export {
  // Response adaptation
  adaptPaginatedResponse,
  adaptEntityResponse,
  adaptErrorResponse,
  adaptCollectionResponse,
  // Data transformation
  flattenNestedArray,
  normalizeCollection,
  denormalizeCollection,
  groupByField,
  extractField,
  filterByField,
  mergeArraysByKey,
  sortByField,
  // Generic mapping
  mapApiResponse,
  transformResponse,
  // Caching
  memoizeAdapter,
  cacheAdapter
} from './adapters'
