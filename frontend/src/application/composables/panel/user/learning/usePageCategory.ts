/**
 * Shared composable for lesson page categorization.
 *
 * Maps lesson titles to categories (theory/practice/assessment)
 * with icons and accent colors.  Single source of truth — used by
 * WorksheetPage, TopBar, Sidebar, and Timeline components.
 */
import { computed, type Ref } from 'vue'
import { useI18n } from 'vue-i18n'

export type PageCategory = 'theory' | 'practice' | 'assessment'

export interface PageCategoryInfo {
  category: PageCategory
  icon: string
  label: string
  accentColor: string
  accentBg: string
}

interface CategoryDef {
  icon: string
  category: PageCategory
}

const TITLE_CATEGORY_MAP: Record<string, CategoryDef> = {
  'erklärung':            { icon: '📖', category: 'theory' },
  'schritt für schritt':  { icon: '📝', category: 'theory' },
  'rechenaufgaben':       { icon: '🔢', category: 'practice' },
  'lückentext':           { icon: '✍️', category: 'practice' },
  'lernkarten':           { icon: '🎴', category: 'practice' },
  'zuordnung':            { icon: '🔄', category: 'practice' },
  'fallstudien':          { icon: '📊', category: 'practice' },
  'ihk-prüfungsaufgaben': { icon: '📋', category: 'assessment' },
}

const CATEGORY_COLORS: Record<PageCategory, { accent: string; bg: string }> = {
  theory:     { accent: '#3b82f6', bg: 'rgba(59, 130, 246, 0.08)' },
  practice:   { accent: '#f59e0b', bg: 'rgba(245, 158, 11, 0.08)' },
  assessment: { accent: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.08)' },
}

const CATEGORY_I18N: Record<PageCategory, string> = {
  theory:     'lessonTimeline.categoryTheory',
  practice:   'lessonTimeline.categoryPractice',
  assessment: 'lessonTimeline.categoryAssessment',
}

/**
 * Detect category from lesson title (lowercase substring match).
 */
export function detectCategory(title: string): CategoryDef | null {
  const lower = title.toLowerCase()
  for (const [key, def] of Object.entries(TITLE_CATEGORY_MAP)) {
    if (lower.includes(key)) return def
  }
  return null
}

/**
 * Reactive composable: returns category info for a lesson.
 */
export function usePageCategory(
  lessonTitle: Ref<string>,
  lessonType: Ref<string>,
) {
  const { t } = useI18n()

  const info = computed<PageCategoryInfo | null>(() => {
    if (lessonType.value !== 'text') return null
    const detected = detectCategory(lessonTitle.value)
    if (!detected) return null
    const colors = CATEGORY_COLORS[detected.category]
    return {
      category: detected.category,
      icon: detected.icon,
      label: t(CATEGORY_I18N[detected.category]),
      accentColor: colors.accent,
      accentBg: colors.bg,
    }
  })

  return { info }
}
