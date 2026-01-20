/**
 * Shared Priority & Severity Constants
 *
 * Central location for priority levels and severity ratings.
 * Used in moderation queues, support tickets, alerts, and triage systems.
 *
 * Usage:
 * import { PRIORITY_LEVELS, SEVERITY_RATINGS } from '@/infrastructure/api/shared/constants'
 *
 * // Use in conditions:
 * if (item.priority === PRIORITY_LEVELS.CRITICAL) { }
 *
 * // Get severity number:
 * const severity = getSeverityValue(PRIORITY_LEVELS.HIGH)  // Returns: 3
 */

/**
 * Priority levels for triage and queuing.
 * Higher = more urgent.
 */
export const PRIORITY_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
  URGENT: 'urgent', // Alias for critical (backward compatibility)
} as const

/**
 * Priority levels mapped to numeric severity values.
 * Useful for sorting and comparing priorities.
 */
export const SEVERITY_RATINGS = {
  LOW: 1,
  MEDIUM: 2,
  HIGH: 3,
  CRITICAL: 4,
  URGENT: 4, // Same as CRITICAL
} as const

/**
 * Priority ordering for sorting.
 * Array index = priority rank (0 = lowest).
 */
export const PRIORITY_ORDER = [
  PRIORITY_LEVELS.LOW,
  PRIORITY_LEVELS.MEDIUM,
  PRIORITY_LEVELS.HIGH,
  PRIORITY_LEVELS.CRITICAL,
] as const

/**
 * SLA (Service Level Agreement) targets by priority.
 * Time in minutes to resolve.
 */
export const PRIORITY_SLA = {
  [PRIORITY_LEVELS.LOW]: 1440, // 24 hours
  [PRIORITY_LEVELS.MEDIUM]: 480, // 8 hours
  [PRIORITY_LEVELS.HIGH]: 120, // 2 hours
  [PRIORITY_LEVELS.CRITICAL]: 30, // 30 minutes
  [PRIORITY_LEVELS.URGENT]: 30, // 30 minutes
} as const

/**
 * Response time expectations by priority.
 * Time in seconds to first response.
 */
export const PRIORITY_RESPONSE_TIME = {
  [PRIORITY_LEVELS.LOW]: 3600, // 1 hour
  [PRIORITY_LEVELS.MEDIUM]: 600, // 10 minutes
  [PRIORITY_LEVELS.HIGH]: 300, // 5 minutes
  [PRIORITY_LEVELS.CRITICAL]: 60, // 1 minute
  [PRIORITY_LEVELS.URGENT]: 60, // 1 minute
} as const

/**
 * Queue positions by priority.
 * Higher = appears earlier in queue.
 * Used for sorting/ordering items in UI.
 */
export const PRIORITY_QUEUE_POSITION = {
  [PRIORITY_LEVELS.CRITICAL]: 1,
  [PRIORITY_LEVELS.URGENT]: 1,
  [PRIORITY_LEVELS.HIGH]: 2,
  [PRIORITY_LEVELS.MEDIUM]: 3,
  [PRIORITY_LEVELS.LOW]: 4,
} as const

/**
 * Get severity value (1-4) for a priority.
 *
 * @param priority - Priority level
 * @returns Severity value (1 = low, 4 = critical)
 *
 * @example
 * getSeverityValue(PRIORITY_LEVELS.HIGH)      // Returns: 3
 * getSeverityValue(PRIORITY_LEVELS.CRITICAL)  // Returns: 4
 */
export function getSeverityValue(priority: string): number {
  return (
    SEVERITY_RATINGS[priority as keyof typeof SEVERITY_RATINGS] || 0
  )
}

/**
 * Compare two priorities.
 *
 * @param p1 - First priority
 * @param p2 - Second priority
 * @returns -1 if p1 < p2, 0 if equal, 1 if p1 > p2
 *
 * @example
 * comparePriorities(PRIORITY_LEVELS.CRITICAL, PRIORITY_LEVELS.MEDIUM)  // Returns: 1
 * comparePriorities(PRIORITY_LEVELS.LOW, PRIORITY_LEVELS.HIGH)        // Returns: -1
 */
export function comparePriorities(p1: string, p2: string): -1 | 0 | 1 {
  const s1 = getSeverityValue(p1)
  const s2 = getSeverityValue(p2)
  return s1 > s2 ? 1 : s1 < s2 ? -1 : 0
}

/**
 * Get human-readable label for priority.
 *
 * @param priority - Priority level
 * @returns Display label
 *
 * @example
 * getPriorityLabel(PRIORITY_LEVELS.CRITICAL)  // Returns: 'Critical'
 * getPriorityLabel(PRIORITY_LEVELS.LOW)       // Returns: 'Low'
 */
export function getPriorityLabel(priority: string): string {
  const labels: Record<string, string> = {
    [PRIORITY_LEVELS.LOW]: 'Low',
    [PRIORITY_LEVELS.MEDIUM]: 'Medium',
    [PRIORITY_LEVELS.HIGH]: 'High',
    [PRIORITY_LEVELS.CRITICAL]: 'Critical',
    [PRIORITY_LEVELS.URGENT]: 'Urgent',
  }
  return labels[priority] || priority
}

/**
 * Get color for priority display.
 *
 * @param priority - Priority level
 * @returns Color code (success, info, warning, error)
 *
 * @example
 * getPriorityColor(PRIORITY_LEVELS.CRITICAL)  // Returns: 'error'
 * getPriorityColor(PRIORITY_LEVELS.LOW)       // Returns: 'success'
 */
export function getPriorityColor(priority: string): string {
  switch (priority) {
    case PRIORITY_LEVELS.CRITICAL:
    case PRIORITY_LEVELS.URGENT:
      return 'error'
    case PRIORITY_LEVELS.HIGH:
      return 'warning'
    case PRIORITY_LEVELS.MEDIUM:
      return 'info'
    case PRIORITY_LEVELS.LOW:
      return 'success'
    default:
      return 'default'
  }
}

/**
 * Get icon for priority display.
 *
 * @param priority - Priority level
 * @returns Icon name (e.g., 'AlertTriangle', 'AlertCircle', 'Info')
 *
 * @example
 * getPriorityIcon(PRIORITY_LEVELS.CRITICAL)  // Returns: 'AlertTriangle'
 * getPriorityIcon(PRIORITY_LEVELS.LOW)       // Returns: 'Info'
 */
export function getPriorityIcon(priority: string): string {
  switch (priority) {
    case PRIORITY_LEVELS.CRITICAL:
    case PRIORITY_LEVELS.URGENT:
      return 'AlertTriangle'
    case PRIORITY_LEVELS.HIGH:
      return 'AlertCircle'
    case PRIORITY_LEVELS.MEDIUM:
      return 'AlertCircle'
    case PRIORITY_LEVELS.LOW:
      return 'Info'
    default:
      return 'Circle'
  }
}

/**
 * Get SLA deadline for a priority.
 *
 * @param priority - Priority level
 * @returns Deadline as Date, or null if priority not found
 *
 * @example
 * const deadline = getSLADeadline(PRIORITY_LEVELS.HIGH)
 * // Returns a Date 2 hours from now
 */
export function getSLADeadline(priority: string): Date | null {
  const minutes = PRIORITY_SLA[priority as keyof typeof PRIORITY_SLA]
  if (!minutes) return null

  const deadline = new Date()
  deadline.setMinutes(deadline.getMinutes() + minutes)
  return deadline
}

/**
 * Check if priority is urgent (critical or urgent).
 *
 * @param priority - Priority level
 * @returns true if urgent
 *
 * @example
 * if (isUrgent(PRIORITY_LEVELS.CRITICAL)) {
 *   // Handle immediately
 * }
 */
export function isUrgent(priority: string): boolean {
  return (
    priority === PRIORITY_LEVELS.CRITICAL ||
    priority === PRIORITY_LEVELS.URGENT
  )
}

/**
 * Check if priority is high severity (high or critical).
 *
 * @param priority - Priority level
 * @returns true if high severity
 *
 * @example
 * if (isHighSeverity(item.priority)) {
 *   // Escalate to manager
 * }
 */
export function isHighSeverity(priority: string): boolean {
  return (
    priority === PRIORITY_LEVELS.HIGH ||
    priority === PRIORITY_LEVELS.CRITICAL ||
    priority === PRIORITY_LEVELS.URGENT
  )
}

/**
 * Sort items by priority (highest first).
 *
 * @param items - Array of items with priority property
 * @param priorityField - Name of priority field (default: 'priority')
 * @returns Sorted array
 *
 * @example
 * const sorted = sortByPriority(tickets, 'priority')
 * // Returns: [critical1, critical2, high1, medium1, ...]
 */
export function sortByPriority<T extends Record<string, any>>(
  items: T[],
  priorityField: keyof T = 'priority' as keyof T
): T[] {
  return [...items].sort((a, b) => {
    const p1 = String(a[priorityField])
    const p2 = String(b[priorityField])
    return comparePriorities(p2, p1) // Reverse order (highest first)
  })
}
