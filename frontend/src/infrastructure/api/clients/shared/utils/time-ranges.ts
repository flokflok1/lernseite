/**
 * Date Range & Duration Utilities
 *
 * Functions for calculating date ranges, durations between dates,
 * and formatting duration as human-readable strings.
 *
 * Usage:
 * import {
 *   getDateRange,
 *   getDuration,
 *   getDurationBreakdown,
 *   formatDuration
 * } from '@/infrastructure/api/shared/utils/time-ranges'
 */

import {
  TIME_UNITS,
  addDays,
  getStartOfDay,
  getEndOfDay,
  getStartOfWeek,
  getEndOfWeek,
  getStartOfMonth,
  getEndOfMonth
} from './time-manipulation'

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
