/**
 * Deadline, SLA & Date Comparison Utilities
 *
 * Functions for SLA deadline calculations, deadline status checks,
 * and date comparison operations (isToday, isPast, isFuture, isSameDay).
 *
 * Usage:
 * import {
 *   calculateSLADeadline,
 *   isDeadlineOverdue,
 *   formatTimeRemaining,
 *   isToday,
 *   isSameDay
 * } from '@/infrastructure/api/shared/utils/time-deadlines'
 */

import { addMinutes } from './time-manipulation'
import { getDuration, getDurationBreakdown } from './time-ranges'

// ============================================
// SLA & Business Time
// ============================================

/**
 * Calculate SLA deadline based on priority and minutes.
 *
 * @param minutes - SLA time in minutes
 * @param fromDate - Start date (default: now)
 * @returns Deadline Date
 *
 * @example
 * calculateSLADeadline(480)  // 8 hours from now
 * calculateSLADeadline(30, startDate)  // 30 minutes from startDate
 */
export function calculateSLADeadline(minutes: number, fromDate: Date = new Date()): Date {
  return addMinutes(fromDate, minutes)
}

/**
 * Check if deadline is overdue.
 *
 * @param deadline - Deadline date
 * @returns true if deadline is in the past
 *
 * @example
 * isDeadlineOverdue(new Date('2020-01-20'))  // true
 * isDeadlineOverdue(new Date('2099-01-20'))  // false
 */
export function isDeadlineOverdue(deadline: Date): boolean {
  return deadline < new Date()
}

/**
 * Get time remaining until deadline.
 *
 * @param deadline - Deadline date
 * @param unit - Time unit (default: 'minutes')
 * @returns Time remaining in specified unit (negative if overdue)
 *
 * @example
 * getTimeRemaining(deadline, 'hours')  // 2.5
 * getTimeRemaining(deadline, 'minutes')  // 150
 */
export function getTimeRemaining(
  deadline: Date,
  unit: 'milliseconds' | 'seconds' | 'minutes' | 'hours' | 'days' = 'minutes'
): number {
  return getDuration(new Date(), deadline, unit)
}

/**
 * Format time remaining as human-readable string.
 *
 * @param deadline - Deadline date
 * @returns Formatted remaining time (e.g., "2 hours remaining" or "overdue by 1 hour")
 *
 * @example
 * formatTimeRemaining(futureDate)  // "2 hours remaining"
 * formatTimeRemaining(pastDate)    // "1 hour overdue"
 */
export function formatTimeRemaining(deadline: Date): string {
  const isOverdue = isDeadlineOverdue(deadline)
  const breakdownDate = isOverdue ? new Date() : deadline
  const startDate = isOverdue ? deadline : new Date()

  const breakdown = getDurationBreakdown(startDate, breakdownDate)
  const parts: string[] = []

  if (breakdown.days > 0) parts.push(`${breakdown.days} day${breakdown.days > 1 ? 's' : ''}`)
  if (breakdown.hours > 0) parts.push(`${breakdown.hours} hour${breakdown.hours > 1 ? 's' : ''}`)
  if (breakdown.minutes > 0)
    parts.push(`${breakdown.minutes} minute${breakdown.minutes > 1 ? 's' : ''}`)

  const timeStr = parts.length > 0 ? parts.join(', ') : '0 minutes'

  return isOverdue ? `${timeStr} overdue` : `${timeStr} remaining`
}

// ============================================
// Comparison & Checks
// ============================================

/**
 * Check if date is today.
 *
 * @param date - Date to check
 * @returns true if date is today
 *
 * @example
 * isToday(new Date())  // true
 * isToday(new Date('2020-01-20'))  // false
 */
export function isToday(date: Date): boolean {
  const today = new Date()
  return (
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
  )
}

/**
 * Check if date is in the past.
 *
 * @param date - Date to check
 * @returns true if date is before now
 *
 * @example
 * isPastDate(new Date('2020-01-20'))  // true
 * isPastDate(new Date('2099-01-20'))  // false
 */
export function isPastDate(date: Date): boolean {
  return date < new Date()
}

/**
 * Check if date is in the future.
 *
 * @param date - Date to check
 * @returns true if date is after now
 *
 * @example
 * isFutureDate(new Date('2099-01-20'))  // true
 * isFutureDate(new Date('2020-01-20'))  // false
 */
export function isFutureDate(date: Date): boolean {
  return date > new Date()
}

/**
 * Check if two dates are on the same day.
 *
 * @param date1 - First date
 * @param date2 - Second date
 * @returns true if both dates are on the same day
 *
 * @example
 * isSameDay(new Date('2026-01-20T10:00'), new Date('2026-01-20T14:30'))  // true
 * isSameDay(new Date('2026-01-20'), new Date('2026-01-21'))  // false
 */
export function isSameDay(date1: Date, date2: Date): boolean {
  return (
    date1.getDate() === date2.getDate() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getFullYear() === date2.getFullYear()
  )
}
