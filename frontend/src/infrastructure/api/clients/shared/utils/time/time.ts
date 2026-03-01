/**
 * Shared Time & Date Utilities
 *
 * Centralized time/date manipulation functions for calculations and conversions.
 * Provides type-safe time operations without external dependencies.
 *
 * Usage:
 * import {
 *   addDays,
 *   getDateRange,
 *   getDuration,
 *   calculateSLA
 * } from '@/infrastructure/api/shared/utils/time'
 *
 * const deadline = calculateSLA('high', new Date())
 * const duration = getDuration(startDate, endDate)
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
// Date Manipulation
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

// ============================================
// Date Range Operations
// ============================================

/**
 * Get date range for specified period.
 *
 * @param period - Period type ('today', 'week', 'month', 'year')
 * @param endDate - End date for range (default: today)
 * @returns Object with fromDate and toDate
 *
 * @example
 * getDateRange('week')  // {
 *   fromDate: 2026-01-19T00:00:00,
 *   toDate: 2026-01-25T23:59:59
 * }
 */
export function getDateRange(
  period: 'today' | 'week' | 'month' | 'year' | 'last-7-days' | 'last-30-days',
  endDate: Date = new Date()
): { fromDate: Date; toDate: Date } {
  switch (period) {
    case 'today':
      return {
        fromDate: getStartOfDay(endDate),
        toDate: getEndOfDay(endDate)
      }

    case 'week':
      return {
        fromDate: getStartOfWeek(endDate),
        toDate: getEndOfWeek(endDate)
      }

    case 'month':
      return {
        fromDate: getStartOfMonth(endDate),
        toDate: getEndOfMonth(endDate)
      }

    case 'year': {
      const year = endDate.getFullYear()
      return {
        fromDate: new Date(year, 0, 1),
        toDate: new Date(year, 11, 31, 23, 59, 59, 999)
      }
    }

    case 'last-7-days':
      return {
        fromDate: addDays(getStartOfDay(endDate), -6),
        toDate: getEndOfDay(endDate)
      }

    case 'last-30-days':
      return {
        fromDate: addDays(getStartOfDay(endDate), -29),
        toDate: getEndOfDay(endDate)
      }

    default:
      return {
        fromDate: getStartOfDay(endDate),
        toDate: getEndOfDay(endDate)
      }
  }
}

// ============================================
// Duration & Difference Calculations
// ============================================

/**
 * Get duration between two dates in different units.
 *
 * @param startDate - Start date
 * @param endDate - End date
 * @param unit - Time unit ('milliseconds', 'seconds', 'minutes', 'hours', 'days')
 * @returns Duration in specified unit
 *
 * @example
 * getDuration(new Date('2026-01-20'), new Date('2026-01-25'), 'days')  // 5
 * getDuration(new Date('10:00'), new Date('12:30'), 'hours')  // 2.5
 */
export function getDuration(
  startDate: Date,
  endDate: Date,
  unit: 'milliseconds' | 'seconds' | 'minutes' | 'hours' | 'days' = 'milliseconds'
): number {
  const diffMs = endDate.getTime() - startDate.getTime()

  switch (unit) {
    case 'milliseconds':
      return diffMs
    case 'seconds':
      return diffMs / TIME_UNITS.SECOND
    case 'minutes':
      return diffMs / TIME_UNITS.MINUTE
    case 'hours':
      return diffMs / TIME_UNITS.HOUR
    case 'days':
      return diffMs / TIME_UNITS.DAY
    default:
      return diffMs
  }
}

/**
 * Get duration as human-readable object (days, hours, minutes, seconds).
 *
 * @param startDate - Start date
 * @param endDate - End date
 * @returns Object with duration breakdown
 *
 * @example
 * getDurationBreakdown(
 *   new Date('2026-01-20T10:00:00'),
 *   new Date('2026-01-23T14:30:45')
 * )
 * // Returns: { days: 3, hours: 4, minutes: 30, seconds: 45 }
 */
export function getDurationBreakdown(
  startDate: Date,
  endDate: Date
): { days: number; hours: number; minutes: number; seconds: number } {
  let diffMs = endDate.getTime() - startDate.getTime()

  if (diffMs < 0) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0 }
  }

  const days = Math.floor(diffMs / TIME_UNITS.DAY)
  diffMs -= days * TIME_UNITS.DAY

  const hours = Math.floor(diffMs / TIME_UNITS.HOUR)
  diffMs -= hours * TIME_UNITS.HOUR

  const minutes = Math.floor(diffMs / TIME_UNITS.MINUTE)
  diffMs -= minutes * TIME_UNITS.MINUTE

  const seconds = Math.floor(diffMs / TIME_UNITS.SECOND)

  return { days, hours, minutes, seconds }
}

/**
 * Format duration as human-readable string.
 *
 * @param startDate - Start date
 * @param endDate - End date
 * @returns Formatted duration string (e.g., "3 days, 4 hours, 30 minutes")
 *
 * @example
 * formatDuration(new Date('2026-01-20'), new Date('2026-01-23T14:30:00'))
 * // Returns: "3 days, 14 hours, 30 minutes"
 */
export function formatDuration(startDate: Date, endDate: Date): string {
  const breakdown = getDurationBreakdown(startDate, endDate)
  const parts: string[] = []

  if (breakdown.days > 0) parts.push(`${breakdown.days} day${breakdown.days > 1 ? 's' : ''}`)
  if (breakdown.hours > 0) parts.push(`${breakdown.hours} hour${breakdown.hours > 1 ? 's' : ''}`)
  if (breakdown.minutes > 0)
    parts.push(`${breakdown.minutes} minute${breakdown.minutes > 1 ? 's' : ''}`)
  if (breakdown.seconds > 0)
    parts.push(`${breakdown.seconds} second${breakdown.seconds > 1 ? 's' : ''}`)

  return parts.length > 0 ? parts.join(', ') : '0 seconds'
}

