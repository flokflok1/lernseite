/**
 * Cache Key Constants
 *
 * Centralized cache key definitions to prevent hardcoded strings.
 * Type-safe access to cache keys throughout the application.
 *
 * Naming Convention:
 * - USER_* for user-related data
 * - COURSE_* for course-related data
 * - THEME_* for theme/preference data
 * - SESSION_* for temporary session data
 *
 * Usage:
 *   const user = cache.get(CACHE_KEYS.USER_PROFILE(userId))
 *   cache.set(CACHE_KEYS.CURRENT_COURSES, courses, 3600)
 */

/**
 * Cache key for user profile
 * TTL: 1 hour (3600s) - user data changes infrequently
 */
export const CACHE_KEY_USER_PROFILE = (userId: string) => `user:profile:${userId}`

/**
 * Cache key for current user
 * TTL: 30 minutes (1800s) - check auth status periodically
 */
export const CACHE_KEY_CURRENT_USER = 'user:current'

/**
 * Cache key for user permissions
 * TTL: 1 hour (3600s) - permissions change infrequently
 */
export const CACHE_KEY_USER_PERMISSIONS = (userId: string) => `user:permissions:${userId}`

/**
 * Cache key for user roles
 * TTL: 2 hours (7200s) - very stable
 */
export const CACHE_KEY_USER_ROLES = (userId: string) => `user:roles:${userId}`

/**
 * Cache key for currently enrolled courses
 * TTL: 30 minutes (1800s) - enrollment status can change
 */
export const CACHE_KEY_CURRENT_COURSES = 'courses:current:user'

/**
 * Cache key for course details
 * TTL: 1 hour (3600s) - course content changes less frequently
 */
export const CACHE_KEY_COURSE_DETAIL = (courseId: string) => `course:detail:${courseId}`

/**
 * Cache key for course chapters
 * TTL: 1 hour (3600s) - structure changes infrequently
 */
export const CACHE_KEY_COURSE_CHAPTERS = (courseId: string) => `course:chapters:${courseId}`

/**
 * Cache key for course lessons
 * TTL: 1 hour (3600s) - lesson structure is stable
 */
export const CACHE_KEY_COURSE_LESSONS = (chapterId: string) => `course:lessons:${chapterId}`

/**
 * Cache key for course progress
 * TTL: 5 minutes (300s) - user progress updates frequently
 */
export const CACHE_KEY_COURSE_PROGRESS = (userId: string, courseId: string) =>
  `course:progress:${userId}:${courseId}`

/**
 * Cache key for learning method definitions
 * TTL: 24 hours (86400s) - learning methods are static
 */
export const CACHE_KEY_LEARNING_METHODS = 'learning:methods:all'

/**
 * Cache key for theme preferences
 * TTL: 30 days (2592000s) - user preferences very stable
 */
export const CACHE_KEY_THEME_PREFERENCE = (userId: string) => `theme:preference:${userId}`

/**
 * Cache key for language preference
 * TTL: 30 days (2592000s) - language choice is very stable
 */
export const CACHE_KEY_LANGUAGE_PREFERENCE = (userId: string) => `language:preference:${userId}`

/**
 * Cache key for user dashboard data
 * TTL: 15 minutes (900s) - dashboard refreshes periodically
 */
export const CACHE_KEY_DASHBOARD_DATA = (userId: string) => `dashboard:${userId}`

/**
 * Cache key for feature flags
 * TTL: 1 hour (3600s) - feature flags change infrequently
 */
export const CACHE_KEY_FEATURE_FLAGS = 'feature:flags:all'

/**
 * Cache key for system notifications
 * TTL: 5 minutes (300s) - notifications are time-sensitive
 */
export const CACHE_KEY_NOTIFICATIONS = (userId: string) => `notifications:${userId}`

/**
 * Cache key for search results (temporary session data)
 * TTL: 10 minutes (600s) - search results are temporary
 */
export const CACHE_KEY_SEARCH_RESULTS = (query: string) => `search:results:${query}`

/**
 * Cache key for API response cache (generic)
 * TTL: 5 minutes (300s) - API responses should refresh periodically
 */
export const CACHE_KEY_API_RESPONSE = (endpoint: string) => `api:response:${endpoint}`

/**
 * Cache key for temporary form state
 * TTL: Session only - form state is temporary
 */
export const CACHE_KEY_FORM_STATE = (formId: string) => `form:state:${formId}`

/**
 * Cache key for temporary upload state
 * TTL: Session only - upload is temporary
 */
export const CACHE_KEY_UPLOAD_STATE = (uploadId: string) => `upload:state:${uploadId}`

/**
 * Cache key for token refresh state
 * TTL: 5 minutes (300s) - short-lived for security
 */
export const CACHE_KEY_TOKEN_REFRESH = 'auth:token:refresh'

/**
 * TTL constants (in seconds)
 */
export const CACHE_TTL = {
  // Very short term - rapid changes
  SHORT: 300,       // 5 minutes
  MEDIUM_SHORT: 600, // 10 minutes

  // Short to medium term - frequent updates
  MEDIUM: 1800,     // 30 minutes
  MEDIUM_LONG: 3600, // 1 hour

  // Long term - infrequent updates
  LONG: 7200,       // 2 hours
  VERY_LONG: 86400, // 24 hours

  // Very long term - almost static
  PERSISTENT: 2592000, // 30 days

  // Session-based
  SESSION: 0,       // No expiry (sessionStorage lifetime)
}

/**
 * Aggregate cache key definitions for convenient access
 */
export const CACHE_KEYS = {
  // User-related
  userProfile: CACHE_KEY_USER_PROFILE,
  currentUser: CACHE_KEY_CURRENT_USER,
  userPermissions: CACHE_KEY_USER_PERMISSIONS,
  userRoles: CACHE_KEY_USER_ROLES,

  // Course-related
  currentCourses: CACHE_KEY_CURRENT_COURSES,
  courseDetail: CACHE_KEY_COURSE_DETAIL,
  courseChapters: CACHE_KEY_COURSE_CHAPTERS,
  courseLessons: CACHE_KEY_COURSE_LESSONS,
  courseProgress: CACHE_KEY_COURSE_PROGRESS,

  // Learning-related
  learningMethods: CACHE_KEY_LEARNING_METHODS,

  // Preferences
  themePreference: CACHE_KEY_THEME_PREFERENCE,
  languagePreference: CACHE_KEY_LANGUAGE_PREFERENCE,

  // Dashboard & UI
  dashboardData: CACHE_KEY_DASHBOARD_DATA,
  featureFlags: CACHE_KEY_FEATURE_FLAGS,
  notifications: CACHE_KEY_NOTIFICATIONS,

  // Temporary/Session
  searchResults: CACHE_KEY_SEARCH_RESULTS,
  apiResponse: CACHE_KEY_API_RESPONSE,
  formState: CACHE_KEY_FORM_STATE,
  uploadState: CACHE_KEY_UPLOAD_STATE,
  tokenRefresh: CACHE_KEY_TOKEN_REFRESH,
} as const
