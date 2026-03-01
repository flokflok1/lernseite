/**
 * Time Utilities - Part 2
 *
 * SLA/business time calculations and date comparison utilities.
 * Split from time.ts for G01 compliance (max 500 LOC).
 */

import { addMinutes, getDuration, getDurationBreakdown } from './time'

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
 * @returns Formatted remaining time (e.g., "2 hours remaining" or "1 hour overdue")
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
 */
export function isPastDate(date: Date): boolean {
  return date < new Date()
}

/**
 * Check if date is in the future.
 */
export function isFutureDate(date: Date): boolean {
  return date > new Date()
}

/**
 * Check if two dates are on the same day.
 */
export function isSameDay(date1: Date, date2: Date): boolean {
  return (
    date1.getDate() === date2.getDate() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getFullYear() === date2.getFullYear()
  )
}
