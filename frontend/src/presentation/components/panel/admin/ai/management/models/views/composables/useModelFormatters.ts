/**
 * useModelFormatters - Formatting utilities for AI model display
 *
 * Provides badge classes, labels, and formatters for cost levels,
 * speed ratings, provider badges, category icons, and token prices.
 */

const CATEGORY_ICONS: Record<string, string> = {
  chat: '\uD83D\uDCAC',
  reasoning: '\uD83E\uDDE0',
  realtime: '\u26A1',
  audio: '\uD83C\uDFB5',
  image: '\uD83D\uDDBC\uFE0F',
  video: '\uD83C\uDFAC',
  embedding: '\uD83D\uDCCA',
  moderation: '\uD83D\uDEE1\uFE0F'
}

const CATEGORY_LABELS: Record<string, string> = {
  chat: 'Chat',
  reasoning: 'Reasoning',
  realtime: 'Realtime',
  audio: 'Audio',
  image: 'Bild',
  video: 'Video',
  embedding: 'Embedding',
  moderation: 'Moderation'
}

const PROVIDER_BADGE_CLASSES: Record<string, string> = {
  openai: 'bg-emerald-100 text-emerald-800',
  anthropic: 'bg-orange-100 text-orange-800',
  google: 'bg-blue-100 text-blue-800',
  mistral: 'bg-purple-100 text-purple-800',
  cohere: 'bg-red-100 text-red-800',
  meta: 'bg-indigo-100 text-indigo-800'
}

const COST_LABELS: Record<string, string> = {
  free: 'Kostenlos',
  low: 'Günstig',
  medium: 'Mittel',
  high: 'Teuer',
  very_high: 'Sehr teuer'
}

const COST_BADGE_CLASSES: Record<string, string> = {
  free: 'bg-[var(--color-success-bg,#d1fae5)] text-[var(--color-success-text,#065f46)]',
  low: 'bg-[var(--color-success-bg,#d1fae5)] text-[var(--color-success-text,#065f46)]',
  medium: 'bg-[var(--color-warning-bg,#fef3c7)] text-[var(--color-warning-text,#92400e)]',
  high: 'bg-[var(--color-error,#dc2626)]/10 text-[var(--color-error,#dc2626)]',
  very_high: 'bg-[var(--color-error,#dc2626)]/20 text-[var(--color-error,#dc2626)]'
}

const SPEED_LABELS: Record<string, string> = {
  very_fast: 'Sehr schnell',
  fast: 'Schnell',
  medium: 'Mittel',
  slow: 'Langsam'
}

const SPEED_BADGE_CLASSES: Record<string, string> = {
  very_fast: 'bg-[var(--color-success-bg,#d1fae5)] text-[var(--color-success-text,#065f46)]',
  fast: 'bg-[var(--color-success-bg,#d1fae5)] text-[var(--color-success-text,#065f46)]',
  medium: 'bg-[var(--color-warning-bg,#fef3c7)] text-[var(--color-warning-text,#92400e)]',
  slow: 'bg-[var(--color-error,#dc2626)]/10 text-[var(--color-error,#dc2626)]'
}

const PROVIDER_ICONS: Record<string, string> = {
  openai: '\uD83D\uDFE2',
  anthropic: '\uD83D\uDFE0',
  google: '\uD83D\uDD35',
  mistral: '\uD83D\uDFE3',
  cohere: '\uD83D\uDD34',
  meta: '\uD83D\uDD37'
}

const DEFAULT_BADGE_CLASS = 'bg-[var(--color-surface)] text-[var(--color-text-secondary)]'
const DEFAULT_BADGE_CLASS_WITH_BORDER = `${DEFAULT_BADGE_CLASS} border border-[var(--color-border)]`

export function useModelFormatters() {
  function getCategoryIcon(category: string): string {
    return CATEGORY_ICONS[category] || '\uD83E\uDD16'
  }

  function getCategoryLabel(category: string): string {
    return CATEGORY_LABELS[category] || category
  }

  function getProviderBadgeClass(provider: string): string {
    return PROVIDER_BADGE_CLASSES[provider] || DEFAULT_BADGE_CLASS_WITH_BORDER
  }

  function getCostLabel(level: string): string {
    return COST_LABELS[level] || level
  }

  function getCostBadgeClass(level: string): string {
    return COST_BADGE_CLASSES[level] || DEFAULT_BADGE_CLASS
  }

  function getSpeedLabel(speed: string): string {
    return SPEED_LABELS[speed] || speed
  }

  function getSpeedBadgeClass(speed: string): string {
    return SPEED_BADGE_CLASSES[speed] || DEFAULT_BADGE_CLASS
  }

  function getProviderIcon(provider: string): string {
    return PROVIDER_ICONS[provider] || '\u26AA'
  }

  function formatContextWindow(tokens: number): string {
    if (tokens >= 1_000_000) {
      return `${(tokens / 1_000_000).toFixed(1)}M`
    }
    if (tokens >= 1_000) {
      return `${Math.round(tokens / 1_000)}K`
    }
    return String(tokens)
  }

  function formatPrice(price: number | string | null | undefined): string {
    if (price === null || price === undefined || price === '') return '-'
    const numPrice = typeof price === 'string' ? parseFloat(price) : price
    if (isNaN(numPrice)) return '-'
    if (numPrice === 0) return 'Kostenlos'
    return `$${numPrice.toFixed(4)}`
  }

  return {
    getCategoryIcon,
    getCategoryLabel,
    getProviderBadgeClass,
    getCostLabel,
    getCostBadgeClass,
    getSpeedLabel,
    getSpeedBadgeClass,
    getProviderIcon,
    formatContextWindow,
    formatPrice
  }
}
