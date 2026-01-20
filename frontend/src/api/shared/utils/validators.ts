/**
 * Shared Validators
 *
 * Centralized validation functions for common patterns across domains.
 * Provides type-safe, reusable validators for email, URLs, dates, enums, etc.
 *
 * Usage:
 * import {
 *   isEmail,
 *   isUrl,
 *   isValidDate,
 *   isValidStatus,
 *   isPriority
 * } from '@/api/shared/utils/validators'
 *
 * if (!isEmail(userEmail)) {
 *   return { error: 'Invalid email format' }
 * }
 */

// ============================================
// Email & URL Validators
// ============================================

/**
 * Check if string is valid email format.
 *
 * @param email - Email string to validate
 * @returns true if valid email format
 *
 * @example
 * isEmail('user@example.com')  // Returns: true
 * isEmail('invalid-email')     // Returns: false
 */
export function isEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Check if string is valid URL.
 *
 * @param url - URL string to validate
 * @returns true if valid URL format
 *
 * @example
 * isUrl('https://example.com')        // Returns: true
 * isUrl('http://localhost:3000/path') // Returns: true
 * isUrl('not-a-url')                  // Returns: false
 */
export function isUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * Check if string is valid absolute URL (http/https).
 *
 * @param url - URL string to validate
 * @returns true if valid absolute URL
 *
 * @example
 * isAbsoluteUrl('https://example.com')  // Returns: true
 * isAbsoluteUrl('/relative/path')       // Returns: false
 */
export function isAbsoluteUrl(url: string): boolean {
  return isUrl(url) && (url.startsWith('http://') || url.startsWith('https://'))
}

// ============================================
// Date Validators
// ============================================

/**
 * Check if string is valid ISO date format (YYYY-MM-DD).
 *
 * @param dateString - Date string to validate
 * @returns true if valid ISO date format
 *
 * @example
 * isValidDate('2026-01-20')    // Returns: true
 * isValidDate('2026/01/20')    // Returns: false
 * isValidDate('invalid-date')  // Returns: false
 */
export function isValidDate(dateString: string): boolean {
  const isoRegex = /^\d{4}-\d{2}-\d{2}$/
  if (!isoRegex.test(dateString)) return false

  const date = new Date(dateString)
  return date instanceof Date && !isNaN(date.getTime())
}

/**
 * Check if date string is valid and in the past.
 *
 * @param dateString - Date string to validate
 * @returns true if valid date and in the past
 *
 * @example
 * isPastDate('2020-01-20')  // Returns: true (if current date is after 2020-01-20)
 * isPastDate('2099-01-20')  // Returns: false (future date)
 */
export function isPastDate(dateString: string): boolean {
  if (!isValidDate(dateString)) return false

  const date = new Date(dateString)
  const now = new Date()

  return date < now
}

/**
 * Check if date string is valid and in the future.
 *
 * @param dateString - Date string to validate
 * @returns true if valid date and in the future
 *
 * @example
 * isFutureDate('2099-01-20')  // Returns: true (if current date is before 2099-01-20)
 * isFutureDate('2020-01-20')  // Returns: false (past date)
 */
export function isFutureDate(dateString: string): boolean {
  if (!isValidDate(dateString)) return false

  const date = new Date(dateString)
  const now = new Date()

  return date > now
}

/**
 * Check if date string is within specified range.
 *
 * @param dateString - Date string to validate
 * @param fromDate - Start of range (inclusive, ISO format)
 * @param toDate - End of range (inclusive, ISO format)
 * @returns true if date is within range
 *
 * @example
 * isDateInRange('2026-06-15', '2026-01-01', '2026-12-31')  // Returns: true
 * isDateInRange('2027-01-01', '2026-01-01', '2026-12-31')  // Returns: false
 */
export function isDateInRange(
  dateString: string,
  fromDate: string,
  toDate: string
): boolean {
  if (!isValidDate(dateString) || !isValidDate(fromDate) || !isValidDate(toDate)) {
    return false
  }

  const date = new Date(dateString)
  const from = new Date(fromDate)
  const to = new Date(toDate)

  return date >= from && date <= to
}

// ============================================
// String Validators
// ============================================

/**
 * Check if string is non-empty and not just whitespace.
 *
 * @param value - String to validate
 * @returns true if non-empty
 *
 * @example
 * isNonEmpty('hello')  // Returns: true
 * isNonEmpty('   ')    // Returns: false
 * isNonEmpty('')       // Returns: false
 */
export function isNonEmpty(value: string): boolean {
  return value.trim().length > 0
}

/**
 * Check if string length is within range.
 *
 * @param value - String to validate
 * @param min - Minimum length (inclusive)
 * @param max - Maximum length (inclusive)
 * @returns true if length is within range
 *
 * @example
 * isLengthInRange('hello', 3, 10)  // Returns: true
 * isLengthInRange('hi', 3, 10)     // Returns: false (too short)
 */
export function isLengthInRange(value: string, min: number, max: number): boolean {
  return value.length >= min && value.length <= max
}

/**
 * Check if string is alphanumeric (letters and numbers only).
 *
 * @param value - String to validate
 * @returns true if alphanumeric
 *
 * @example
 * isAlphanumeric('user123')    // Returns: true
 * isAlphanumeric('user-123')   // Returns: false (contains hyphen)
 */
export function isAlphanumeric(value: string): boolean {
  return /^[a-zA-Z0-9]+$/.test(value)
}

/**
 * Check if string is alphanumeric with underscores and hyphens.
 *
 * @param value - String to validate
 * @returns true if slug-like
 *
 * @example
 * isSlug('user-name_123')  // Returns: true
 * isSlug('user name')      // Returns: false (contains space)
 */
export function isSlug(value: string): boolean {
  return /^[a-zA-Z0-9_-]+$/.test(value)
}

/**
 * Check if string contains only lowercase letters, numbers, hyphens.
 *
 * @param value - String to validate
 * @returns true if valid kebab-case
 *
 * @example
 * isKebabCase('user-profile')  // Returns: true
 * isKebabCase('userProfile')   // Returns: false (camelCase)
 */
export function isKebabCase(value: string): boolean {
  return /^[a-z0-9]+(-[a-z0-9]+)*$/.test(value)
}

// ============================================
// Number & Quantity Validators
// ============================================

/**
 * Check if value is a valid positive integer.
 *
 * @param value - Value to validate
 * @returns true if positive integer
 *
 * @example
 * isPositiveInteger(5)    // Returns: true
 * isPositiveInteger(0)    // Returns: false
 * isPositiveInteger(-5)   // Returns: false
 * isPositiveInteger(5.5)  // Returns: false
 */
export function isPositiveInteger(value: unknown): boolean {
  return Number.isInteger(value) && typeof value === 'number' && value > 0
}

/**
 * Check if value is a valid non-negative integer.
 *
 * @param value - Value to validate
 * @returns true if non-negative integer
 *
 * @example
 * isNonNegativeInteger(5)   // Returns: true
 * isNonNegativeInteger(0)   // Returns: true
 * isNonNegativeInteger(-5)  // Returns: false
 */
export function isNonNegativeInteger(value: unknown): boolean {
  return Number.isInteger(value) && typeof value === 'number' && value >= 0
}

/**
 * Check if value is within specified range.
 *
 * @param value - Value to validate
 * @param min - Minimum value (inclusive)
 * @param max - Maximum value (inclusive)
 * @returns true if within range
 *
 * @example
 * isNumberInRange(5, 0, 10)    // Returns: true
 * isNumberInRange(0, 0, 10)    // Returns: true
 * isNumberInRange(-1, 0, 10)   // Returns: false
 */
export function isNumberInRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max
}

/**
 * Check if value is percentage (0-100).
 *
 * @param value - Value to validate
 * @returns true if valid percentage
 *
 * @example
 * isPercentage(50)    // Returns: true
 * isPercentage(100)   // Returns: true
 * isPercentage(101)   // Returns: false
 * isPercentage(-1)    // Returns: false
 */
export function isPercentage(value: unknown): boolean {
  return isNumberInRange(value as number, 0, 100)
}

// ============================================
// Enum & Status Validators
// ============================================

/**
 * Check if value is one of allowed values.
 *
 * @param value - Value to validate
 * @param allowedValues - Array of allowed values
 * @returns true if value is in allowed list
 *
 * @example
 * isEnumValue('pending', ['pending', 'active', 'resolved'])  // Returns: true
 * isEnumValue('invalid', ['pending', 'active', 'resolved'])  // Returns: false
 */
export function isEnumValue<T>(value: unknown, allowedValues: readonly T[]): boolean {
  return allowedValues.includes(value as T)
}

/**
 * Check if value is valid status from constant object.
 *
 * @param value - Status value to validate
 * @param statusObject - Status constant object (e.g., MODERATION_STATUS)
 * @returns true if value is valid status
 *
 * @example
 * import { MODERATION_STATUS } from '@/api/shared/constants'
 * isValidStatus('pending', MODERATION_STATUS)  // Returns: true
 * isValidStatus('invalid', MODERATION_STATUS)  // Returns: false
 */
export function isValidStatus(
  value: unknown,
  statusObject: Record<string, string>
): boolean {
  const statusValues = Object.values(statusObject)
  return statusValues.includes(value as string)
}

/**
 * Check if value is valid priority level.
 *
 * @param value - Priority value to validate
 * @param priorityLevels - Priority object (e.g., PRIORITY_LEVELS)
 * @returns true if valid priority
 *
 * @example
 * import { PRIORITY_LEVELS } from '@/api/shared/constants'
 * isPriority('high', PRIORITY_LEVELS)  // Returns: true
 * isPriority('invalid', PRIORITY_LEVELS)  // Returns: false
 */
export function isPriority(
  value: unknown,
  priorityLevels: Record<string, string>
): boolean {
  const priorityValues = Object.values(priorityLevels)
  return priorityValues.includes(value as string)
}

// ============================================
// Array & Collection Validators
// ============================================

/**
 * Check if array is non-empty.
 *
 * @param arr - Array to validate
 * @returns true if array has at least one element
 *
 * @example
 * isNonEmptyArray([1, 2, 3])  // Returns: true
 * isNonEmptyArray([])         // Returns: false
 */
export function isNonEmptyArray<T>(arr: T[]): boolean {
  return Array.isArray(arr) && arr.length > 0
}

/**
 * Check if array length is within range.
 *
 * @param arr - Array to validate
 * @param min - Minimum length (inclusive)
 * @param max - Maximum length (inclusive)
 * @returns true if length is within range
 *
 * @example
 * isArrayLengthInRange([1, 2, 3], 2, 5)  // Returns: true
 * isArrayLengthInRange([1], 2, 5)        // Returns: false (too short)
 */
export function isArrayLengthInRange<T>(arr: T[], min: number, max: number): boolean {
  return Array.isArray(arr) && arr.length >= min && arr.length <= max
}

/**
 * Check if array contains unique values (no duplicates).
 *
 * @param arr - Array to validate
 * @returns true if all values are unique
 *
 * @example
 * isArrayUnique([1, 2, 3])      // Returns: true
 * isArrayUnique([1, 2, 2, 3])   // Returns: false
 */
export function isArrayUnique<T>(arr: T[]): boolean {
  return new Set(arr).size === arr.length
}

// ============================================
// Object Validators
// ============================================

/**
 * Check if value is valid object (not null, not array).
 *
 * @param value - Value to validate
 * @returns true if valid object
 *
 * @example
 * isObject({})        // Returns: true
 * isObject([])        // Returns: false
 * isObject(null)      // Returns: false
 * isObject('string')  // Returns: false
 */
export function isObject(value: unknown): boolean {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

/**
 * Check if object has required keys.
 *
 * @param obj - Object to validate
 * @param requiredKeys - Keys that must be present
 * @returns true if all required keys are present
 *
 * @example
 * const user = { id: '1', name: 'John', email: 'john@example.com' }
 * isObjectWithKeys(user, ['id', 'name'])    // Returns: true
 * isObjectWithKeys(user, ['id', 'age'])     // Returns: false (missing 'age')
 */
export function isObjectWithKeys(
  obj: unknown,
  requiredKeys: string[]
): boolean {
  if (!isObject(obj)) return false

  const objectKeys = Object.keys(obj as Record<string, unknown>)
  return requiredKeys.every((key) => objectKeys.includes(key))
}

/**
 * Check if all object values are non-empty strings.
 *
 * @param obj - Object to validate
 * @returns true if all values are non-empty strings
 *
 * @example
 * isObjectWithStringValues({ name: 'John', city: 'NYC' })        // Returns: true
 * isObjectWithStringValues({ name: 'John', city: '' })           // Returns: false
 * isObjectWithStringValues({ name: 'John', age: 30 })            // Returns: false
 */
export function isObjectWithStringValues(obj: unknown): boolean {
  if (!isObject(obj)) return false

  return Object.values(obj as Record<string, unknown>).every(
    (value) => typeof value === 'string' && value.length > 0
  )
}
