/**
 * Date Manipulation Utilities
 *
 * Core date manipulation functions: adding time units, and getting
 * start/end boundaries of days, weeks, and months.
 *
 * Usage:
 * import {
 *   TIME_UNITS,
 *   addDays,
 *   addHours,
 *   getStartOfDay,
 *   getEndOfMonth
 * } from '@/infrastructure/api/shared/utils/time-manipulation'
 */

// ============================================
// Time Constants
// ============================================

export const TIME_UNITS = {
  MILLISECOND: 1,
  SECOND: 1000,
  MINUTE: 60 * 1000,
  HOUR: 60 * 60 * 1000,
  DAY: 24 * 60 * 60 * 1000,
  WEEK: 7 * 24 * 60 * 60 * 1000,
  MONTH: 30 * 24 * 60 * 60 * 1000,
  YEAR: 365 * 24 * 60 * 60 * 1000
} as const

// ============================================
// Date Arithmetic
// ============================================

/**
 * Add days to date.
 *
 * @param date - Base date
 * @param days - Number of days to add (can be negative)
 * @returns New Date object
 *
 * @example
 * addDays(new Date('2026-01-20'), 5)  // 2026-01-25
 * addDays(new Date('2026-01-20'), -3) // 2026-01-17
 */
export function addDays(date: Date, days: number): Date {
  const result = new Date(date)
  result.setDate(result.getDate() + days)
  return result
}

/**
 * Add hours to date.
 *
 * @param date - Base date
 * @param hours - Number of hours to add (can be negative)
 * @returns New Date object
 *
 * @example
 * addHours(new Date('2026-01-20T12:00:00'), 2)  // 14:00
 * addHours(new Date('2026-01-20T12:00:00'), -1) // 11:00
 */
export function addHours(date: Date, hours: number): Date {
  const result = new Date(date)
  result.setHours(result.getHours() + hours)
  return result
}

/**
 * Add minutes to date.
 *
 * @param date - Base date
 * @param minutes - Number of minutes to add (can be negative)
 * @returns New Date object
 *
 * @example
 * addMinutes(new Date(), 30)
 * addMinutes(new Date(), -15)
 */
export function addMinutes(date: Date, minutes: number): Date {
  const result = new Date(date)
  result.setMinutes(result.getMinutes() + minutes)
  return result
}

/**
 * Add months to date.
 *
 * @param date - Base date
 * @param months - Number of months to add (can be negative)
 * @returns New Date object
 *
 * @example
 * addMonths(new Date('2026-01-20'), 3)  // 2026-04-20
 * addMonths(new Date('2026-01-20'), -1) // 2025-12-20
 */
export function addMonths(date: Date, months: number): Date {
  const result = new Date(date)
  result.setMonth(result.getMonth() + months)
  return result
}

/**
 * Add years to date.
 *
 * @param date - Base date
 * @param years - Number of years to add (can be negative)
 * @returns New Date object
 *
 * @example
 * addYears(new Date('2026-01-20'), 1)  // 2027-01-20
 */
export function addYears(date: Date, years: number): Date {
  const result = new Date(date)
  result.setFullYear(result.getFullYear() + years)
  return result
}

// ============================================
// Period Boundaries
// ============================================

/**
 * Get start of day (00:00:00).
 *
 * @param date - Date to get start of
 * @returns Date at start of day
 *
 * @example
 * getStartOfDay(new Date('2026-01-20T14:30:45'))  // 2026-01-20T00:00:00
 */
export function getStartOfDay(date: Date): Date {
  const result = new Date(date)
  result.setHours(0, 0, 0, 0)
  return result
}

/**
 * Get end of day (23:59:59).
 *
 * @param date - Date to get end of
 * @returns Date at end of day
 *
 * @example
 * getEndOfDay(new Date('2026-01-20T14:30:45'))  // 2026-01-20T23:59:59
 */
export function getEndOfDay(date: Date): Date {
  const result = new Date(date)
  result.setHours(23, 59, 59, 999)
  return result
}

/**
 * Get start of week (Monday 00:00:00).
 *
 * @param date - Date to get start of week for
 * @returns Date at start of week
 *
 * @example
 * getStartOfWeek(new Date('2026-01-20'))  // 2026-01-19 (Monday)
 */
export function getStartOfWeek(date: Date): Date {
  const result = new Date(date)
  const day = result.getDay() || 7 // Sunday = 0, convert to 7
  result.setDate(result.getDate() - day + 1)
  result.setHours(0, 0, 0, 0)
  return result
}

/**
 * Get end of week (Sunday 23:59:59).
 *
 * @param date - Date to get end of week for
 * @returns Date at end of week
 *
 * @example
 * getEndOfWeek(new Date('2026-01-20'))  // 2026-01-25 23:59:59 (Sunday)
 */
export function getEndOfWeek(date: Date): Date {
  const result = new Date(date)
  const day = result.getDay() || 7
  result.setDate(result.getDate() - day + 7)
  result.setHours(23, 59, 59, 999)
  return result
}

/**
 * Get start of month (1st day, 00:00:00).
 *
 * @param date - Date to get start of month for
 * @returns Date at start of month
 *
 * @example
 * getStartOfMonth(new Date('2026-01-20'))  // 2026-01-01T00:00:00
 */
export function getStartOfMonth(date: Date): Date {
  const result = new Date(date)
  result.setDate(1)
  result.setHours(0, 0, 0, 0)
  return result
}

/**
 * Get end of month (last day, 23:59:59).
 *
 * @param date - Date to get end of month for
 * @returns Date at end of month
 *
 * @example
 * getEndOfMonth(new Date('2026-01-20'))  // 2026-01-31T23:59:59
 */
export function getEndOfMonth(date: Date): Date {
  const result = new Date(date)
  result.setMonth(result.getMonth() + 1)
  result.setDate(0)
  result.setHours(23, 59, 59, 999)
  return result
}
