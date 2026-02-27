/**
 * Composable for chapter preview logic.
 *
 * Provides computed stats, method icon/name lookups, date formatting,
 * and the "open in user mode" action. Shared across ChapterPreview,
 * ChapterPreviewWindow, and ChapterPreviewPanel.
 */

import { computed, type Ref } from 'vue'
import { useI18n } from 'vue-i18n'

/** Method icon lookup by numeric type ID. */
const METHOD_ICONS: Record<number, string> = {
  0: '\uD83D\uDCD6', 1: '\uD83D\uDCDD', 2: '\uD83D\uDD04', 3: '\uD83D\uDCCA', 4: '\uD83D\uDCAD',
  6: '\uD83C\uDFAF', 8: '\u270F\uFE0F', 9: '\uD83D\uDCBB', 10: '\uD83C\uDF10', 11: '\uD83D\uDD27',
  12: '\uD83D\uDD22', 13: '\uD83C\uDCCF', 14: '\uD83C\uDFAF', 15: '\uD83D\uDCDD', 16: '\uD83D\uDD0D',
  17: '\uD83D\uDEE0\uFE0F', 18: '\u270D\uFE0F', 19: '\uD83D\uDCCB', 20: '\uD83D\uDCD1', 21: '\u23F1\uFE0F',
  22: '\u2753', 23: '\u2705', 24: '\uD83C\uDF64', 25: '\uD83C\uDFC6',
  26: '\uD83D\uDC65', 27: '\uD83E\uDD1D', 28: '\uD83D\uDCCA', 29: '\uD83D\uDCD3', 30: '\uD83D\uDCC1',
  31: '\uD83C\uDF93', 32: '\uD83D\uDD04'
}

export interface UniqueMethod {
  type: number
  count: number
}

/**
 * Parses a method type value (string or number) into a numeric type.
 * Returns NaN if the value cannot be parsed.
 */
function parseMethodType(type: number | string | undefined | null): number {
  if (type === undefined || type === null) return NaN
  if (typeof type === 'string') return parseInt(type, 10)
  return type
}

/**
 * Returns the icon for a given learning method type.
 */
export function getMethodIcon(type: number | string | undefined): string {
  const numType = parseMethodType(type)
  if (isNaN(numType)) return '\uD83D\uDCDA'
  return METHOD_ICONS[numType] || '\uD83D\uDCDA'
}

/**
 * Returns the localized display name for a given learning method type.
 */
export function getMethodName(
  type: number | string | undefined,
  t: (key: string) => string
): string {
  const numType = parseMethodType(type)
  if (isNaN(numType)) return 'LM'
  return t(`lesson.methodExecution.methods.lm${String(numType).padStart(2, '0')}`)
}

/**
 * Composable providing chapter preview computed properties and actions.
 *
 * @param chapter - Reactive reference to the chapter data object
 */
export function useChapterPreview(chapter: Ref<any>) {
  const { t, locale } = useI18n()

  const lessonsCount = computed((): number => {
    return chapter.value?.lessons?.length || 0
  })

  const methodsCount = computed((): number => {
    if (!chapter.value?.lessons) return 0
    return chapter.value.lessons.reduce((sum: number, lesson: any) => {
      return sum + (lesson.methods?.length || 0)
    }, 0)
  })

  const totalDuration = computed((): number => {
    if (!chapter.value?.lessons) return 0
    return chapter.value.lessons.reduce((sum: number, lesson: any) => {
      return sum + (lesson.duration_minutes || 0)
    }, 0)
  })

  const uniqueMethods = computed((): UniqueMethod[] => {
    if (!chapter.value?.lessons) return []

    const methodCounts: Record<number, number> = {}
    chapter.value.lessons.forEach((lesson: any) => {
      lesson.methods?.forEach((method: any) => {
        const numType = parseMethodType(method.type)
        if (!isNaN(numType)) {
          methodCounts[numType] = (methodCounts[numType] || 0) + 1
        }
      })
    })

    return Object.entries(methodCounts)
      .map(([type, count]) => ({ type: parseInt(type, 10), count }))
      .sort((a, b) => b.count - a.count)
  })

  function formatDate(dateStr?: string): string {
    if (!dateStr) return t('chapterPreview.unknown')
    const localeMap: Record<string, string> = { de: 'de-DE', en: 'en-US', pl: 'pl-PL' }
    return new Date(dateStr).toLocaleDateString(localeMap[locale.value] || 'de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  }

  function openInUserMode(): void {
    const chapterId = chapter.value?.chapter_id || chapter.value?.id
    if (chapterId) {
      window.open(`/chapter/${chapterId}`, '_blank')
    }
  }

  return {
    lessonsCount,
    methodsCount,
    totalDuration,
    uniqueMethods,
    formatDate,
    openInUserMode,
    getMethodIcon,
    getMethodName
  }
}
