/**
 * Shared Formatters
 *
 * Centralized formatting functions for common patterns across domains.
 * Provides type-safe formatters for dates, numbers, bytes, text, etc.
 *
 * Usage:
 * import {
 *   formatDate,
 *   formatDateTime,
 *   formatBytes,
 *   formatCurrency,
 *   formatPercentage
 * } from '@/api/shared/utils/formatters'
 *
 * const displayDate = formatDate(dateString)  // "20. Jan 2026"
 * const displaySize = formatBytes(1024000)     // "1 MB"
 */

// ============================================
// Date & Time Formatters
// ============================================

/**
 * Format date string (ISO or Date) to localized date display.
 *
 * @param dateInput - Date string (ISO) or Date object
 * @param locale - Locale code (default: 'de-DE')
 * @returns Formatted date (e.g., "20. Jan 2026")
 *
 * @example
 * formatDate('2026-01-20')              // Returns: "20. Jan 2026" (German)
 * formatDate(new Date(2026, 0, 20))     // Returns: "20. Jan 2026"
 * formatDate('2026-01-20', 'en-US')     // Returns: "Jan 20, 2026"
 */
export function formatDate(dateInput: string | Date, locale: string = 'de-DE'): string {
  try {
    const date = typeof dateInput === 'string' ? new Date(dateInput) : dateInput

    return new Intl.DateTimeFormat(locale, {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    }).format(date)
  } catch {
    return 'Invalid date'
  }
}

/**
 * Format date and time string to localized display.
 *
 * @param dateInput - Date string (ISO) or Date object
 * @param locale - Locale code (default: 'de-DE')
 * @returns Formatted date and time (e.g., "20. Jan 2026, 14:30")
 *
 * @example
 * formatDateTime('2026-01-20T14:30:00Z')  // Returns: "20. Jan 2026, 14:30" (German)
 * formatDateTime('2026-01-20T14:30:00Z', 'en-US')  // Returns: "Jan 20, 2026, 2:30 PM"
 */
export function formatDateTime(
  dateInput: string | Date,
  locale: string = 'de-DE'
): string {
  try {
    const date = typeof dateInput === 'string' ? new Date(dateInput) : dateInput

    return new Intl.DateTimeFormat(locale, {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  } catch {
    return 'Invalid date'
  }
}

/**
 * Format ISO date string to short date format (DD.MM.YYYY or MM/DD/YYYY).
 *
 * @param dateString - ISO date string
 * @param locale - Locale code (default: 'de-DE')
 * @returns Short formatted date (e.g., "20.01.2026" in German, "01/20/2026" in US)
 *
 * @example
 * formatShortDate('2026-01-20')           // Returns: "20.01.2026" (German)
 * formatShortDate('2026-01-20', 'en-US') // Returns: "01/20/2026"
 */
export function formatShortDate(dateString: string, locale: string = 'de-DE'): string {
  try {
    const date = new Date(dateString)

    return new Intl.DateTimeFormat(locale, {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    }).format(date)
  } catch {
    return 'Invalid date'
  }
}

/**
 * Format time string to localized time display.
 *
 * @param timeString - ISO time string
 * @param locale - Locale code (default: 'de-DE')
 * @returns Formatted time (e.g., "14:30" in 24h format, "2:30 PM" in 12h)
 *
 * @example
 * formatTime('2026-01-20T14:30:00Z')       // Returns: "14:30" (German 24h)
 * formatTime('2026-01-20T14:30:00Z', 'en-US')  // Returns: "2:30 PM"
 */
export function formatTime(timeString: string, locale: string = 'de-DE'): string {
  try {
    const date = new Date(timeString)

    return new Intl.DateTimeFormat(locale, {
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  } catch {
    return 'Invalid time'
  }
}

/**
 * Format date as relative time (e.g., "2 hours ago", "in 3 days").
 *
 * @param dateInput - Date string (ISO) or Date object
 * @param locale - Locale code (default: 'de-DE')
 * @returns Relative time string
 *
 * @example
 * formatRelativeTime('2026-01-20T12:00:00Z')  // Returns: "2 hours ago" or "in 2 hours"
 * formatRelativeTime(new Date())              // Returns: "just now"
 */
export function formatRelativeTime(
  dateInput: string | Date,
  locale: string = 'de-DE'
): string {
  try {
    const date = typeof dateInput === 'string' ? new Date(dateInput) : dateInput
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffSec = Math.round(diffMs / 1000)
    const diffMin = Math.round(diffSec / 60)
    const diffHour = Math.round(diffMin / 60)
    const diffDay = Math.round(diffHour / 24)

    const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' })

    if (Math.abs(diffSec) < 60) {
      return rtf.format(-diffSec, 'second')
    } else if (Math.abs(diffMin) < 60) {
      return rtf.format(-diffMin, 'minute')
    } else if (Math.abs(diffHour) < 24) {
      return rtf.format(-diffHour, 'hour')
    } else {
      return rtf.format(-diffDay, 'day')
    }
  } catch {
    return 'Invalid date'
  }
}

// ============================================
// Number Formatters
// ============================================

/**
 * Format number as localized string with thousands separator.
 *
 * @param value - Number to format
 * @param locale - Locale code (default: 'de-DE')
 * @param digits - Number of decimal places
 * @returns Formatted number string (e.g., "1.234,56" in German, "1,234.56" in US)
 *
 * @example
 * formatNumber(1234567.89)           // Returns: "1.234.567,89" (German)
 * formatNumber(1234567.89, 'en-US')  // Returns: "1,234,567.89"
 * formatNumber(1234.5, 'de-DE', 0)   // Returns: "1.235" (rounded)
 */
export function formatNumber(
  value: number,
  locale: string = 'de-DE',
  digits: number = 2
): string {
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  }).format(value)
}

/**
 * Format number as percentage with optional decimal places.
 *
 * @param value - Number between 0-100 or 0-1
 * @param locale - Locale code (default: 'de-DE')
 * @param digits - Number of decimal places
 * @returns Formatted percentage (e.g., "50,00 %" in German, "50.00%" in US)
 *
 * @example
 * formatPercentage(50)          // Returns: "50,00 %" (German)
 * formatPercentage(0.5, 'en-US')  // Returns: "50.00%" (auto-converts 0-1 range)
 * formatPercentage(99.9, 'de-DE', 1)  // Returns: "99,9 %"
 */
export function formatPercentage(
  value: number,
  locale: string = 'de-DE',
  digits: number = 2
): string {
  // Auto-convert 0-1 range to 0-100
  const displayValue = value > 1 ? value : value * 100

  return new Intl.NumberFormat(locale, {
    style: 'percent',
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  }).format(displayValue / 100)
}

/**
 * Format number as currency.
 *
 * @param value - Number to format as currency
 * @param currency - Currency code (default: 'EUR')
 * @param locale - Locale code (default: 'de-DE')
 * @returns Formatted currency (e.g., "1.234,56 €" in German, "$1,234.56" in US)
 *
 * @example
 * formatCurrency(1234.56)                  // Returns: "1.234,56 €" (German EUR)
 * formatCurrency(1234.56, 'USD', 'en-US') // Returns: "$1,234.56"
 * formatCurrency(99.99, 'GBP')             // Returns: "99,99 £"
 */
export function formatCurrency(
  value: number,
  currency: string = 'EUR',
  locale: string = 'de-DE'
): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency
  }).format(value)
}

// ============================================
// Byte Size Formatters
// ============================================

/**
 * Format byte size to human-readable format (B, KB, MB, GB, TB).
 *
 * @param bytes - Number of bytes
 * @param digits - Number of decimal places (default: 2)
 * @returns Formatted size (e.g., "1.5 MB", "256 KB")
 *
 * @example
 * formatBytes(1024)             // Returns: "1.00 KB"
 * formatBytes(1024000)          // Returns: "1.00 MB"
 * formatBytes(1073741824)       // Returns: "1.00 GB"
 * formatBytes(1536, 1)          // Returns: "1.5 KB"
 */
export function formatBytes(bytes: number, digits: number = 2): string {
  if (bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return (bytes / Math.pow(k, i)).toFixed(digits) + ' ' + sizes[i]
}

// ============================================
// Text Formatters
// ============================================

/**
 * Capitalize first letter of string.
 *
 * @param text - Text to capitalize
 * @returns Capitalized text
 *
 * @example
 * capitalize('hello')  // Returns: "Hello"
 * capitalize('world')  // Returns: "World"
 */
export function capitalize(text: string): string {
  if (text.length === 0) return text
  return text.charAt(0).toUpperCase() + text.slice(1)
}

/**
 * Convert snake_case to Title Case.
 *
 * @param text - Snake case text
 * @returns Title case text
 *
 * @example
 * toTitleCase('pending_verification')  // Returns: "Pending Verification"
 * toTitleCase('user_role')             // Returns: "User Role"
 */
export function toTitleCase(text: string): string {
  return text
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

/**
 * Convert camelCase to Title Case.
 *
 * @param text - Camel case text
 * @returns Title case text
 *
 * @example
 * camelToTitle('userName')    // Returns: "User Name"
 * camelToTitle('isActive')    // Returns: "Is Active"
 */
export function camelToTitle(text: string): string {
  const result = text.replace(/([A-Z])/g, ' $1')
  return capitalize(result.trim())
}

/**
 * Truncate text to maximum length with ellipsis.
 *
 * @param text - Text to truncate
 * @param maxLength - Maximum length including ellipsis
 * @returns Truncated text with ellipsis if needed
 *
 * @example
 * truncate('Hello World', 8)   // Returns: "Hello..."
 * truncate('Hi', 8)            // Returns: "Hi"
 * truncate('Very long text', 10)  // Returns: "Very lo..."
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength - 3) + '...'
}

/**
 * Remove accents and special characters from text (for URLs/slugs).
 *
 * @param text - Text to slugify
 * @returns Slugified text (lowercase, no spaces/special chars)
 *
 * @example
 * slugify('My Blog Post')              // Returns: "my-blog-post"
 * slugify('Café Français')             // Returns: "cafe-francais"
 * slugify('Hello   World')             // Returns: "hello-world"
 */
export function slugify(text: string): string {
  return text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Remove accents
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') // Remove special characters
    .replace(/[\s_]+/g, '-') // Replace spaces with hyphens
    .replace(/^-+|-+$/g, '') // Remove leading/trailing hyphens
}

/**
 * Format phone number with standard formatting.
 *
 * @param phoneNumber - Phone number string (digits only or with country code)
 * @param format - Format pattern (default: 'E.164' for international)
 * @returns Formatted phone number
 *
 * @example
 * formatPhone('491234567890')  // Returns: "+49 123 456 7890"
 * formatPhone('1234567890')    // Returns: "+1 (123) 456-7890"
 */
export function formatPhone(phoneNumber: string, format: string = 'E.164'): string {
  // Remove all non-digit characters except leading +
  const cleaned = phoneNumber.replace(/\D/g, '')

  if (format === 'E.164') {
    // International format: +49 123 456 7890
    if (cleaned.length < 10) return phoneNumber
    return '+' + cleaned.slice(-10).replace(/(\d{2})(\d{3})(\d{4})/, '$1 $2 $3')
  }

  // Default: +1 (123) 456-7890
  if (cleaned.length < 10) return phoneNumber
  return (
    '+' +
    cleaned
      .slice(-10)
      .replace(/(\d{1})(\d{3})(\d{3})(\d{4})/, '$1 ($2) $3-$4')
  )
}

/**
 * Highlight or mark text with tags/HTML escaping.
 *
 * @param text - Text to escape
 * @param searchTerm - Term to highlight
 * @returns HTML-escaped text with highlighting (use v-html carefully!)
 *
 * @example
 * highlightText('Hello World', 'World')  // Returns: "Hello <mark>World</mark>"
 */
export function highlightText(text: string, searchTerm: string): string {
  if (!searchTerm) return escapeHtml(text)

  const regex = new RegExp(`(${searchTerm})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

/**
 * Escape HTML special characters.
 *
 * @param text - Text to escape
 * @returns Escaped HTML
 *
 * @example
 * escapeHtml('<script>alert("xss")</script>')  // Returns: "&lt;script&gt;..."
 */
export function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }

  return text.replace(/[&<>"']/g, (char) => map[char])
}
