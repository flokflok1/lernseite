<template>
  <div
    class="theory-accordion-item rounded-xl overflow-hidden transition-all duration-200"
    :class="expanded
      ? 'border-2 border-blue-400/50 dark:border-blue-500/30 shadow-lg shadow-blue-500/10 dark:shadow-blue-500/5 bg-white dark:bg-gray-800'
      : 'border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 bg-white dark:bg-gray-800/80 hover:shadow-md'"
  >
    <!-- Header -->
    <button
      class="w-full flex items-center justify-between gap-3 px-4 py-3 text-left transition-colors group"
      @click="emit('toggle')"
    >
      <div class="flex items-center gap-3.5 min-w-0">
        <!-- Colored icon -->
        <div
          class="flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center transition-colors"
          :class="expanded
            ? 'bg-blue-500 text-white'
            : 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 group-hover:bg-blue-200 dark:group-hover:bg-blue-900/50'"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <!-- Title + subtitle -->
        <div class="min-w-0">
          <h3 class="font-semibold text-gray-900 dark:text-white truncate text-sm">
            {{ theory.title || $t('chapterTheory.theorySheet') }}
          </h3>
          <p v-if="theory.createdAt" class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
            {{ formatDate(theory.createdAt) }}
          </p>
        </div>
      </div>

      <div class="flex items-center gap-2 flex-shrink-0">
        <!-- Style badge -->
        <span
          v-if="theory.style"
          class="text-xs px-2.5 py-1 rounded-full font-medium"
          :class="styleBadgeClass"
        >
          {{ $t(`chapterTheory.styles.${theory.style}`, theory.style) }}
        </span>
        <!-- Expand chevron -->
        <svg
          class="h-5 w-5 text-gray-400 transition-transform duration-200"
          :class="{ 'rotate-180 text-blue-500': expanded }"
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </button>

    <!-- Content (expandable) -->
    <div v-if="expanded" class="border-t border-gray-100 dark:border-gray-700/50 px-4 py-4">
      <!-- Loading -->
      <div v-if="contentLoading" class="flex flex-col items-center justify-center py-10">
        <div class="relative">
          <div class="animate-spin rounded-full h-10 w-10 border-2 border-blue-200 dark:border-blue-800 border-t-blue-600 dark:border-t-blue-400"></div>
        </div>
        <span class="mt-3 text-sm text-gray-500 dark:text-gray-400">{{ $t('chapterTheory.loadingContent') }}</span>
      </div>

      <!-- Content -->
      <div v-else-if="content" class="theory-content space-y-5">
        <!-- Manual content -->
        <div v-if="content.content" class="prose dark:prose-invert max-w-none" v-html="sanitize(formatContent(content.content))"></div>

        <!-- AI blocks -->
        <template v-else>
          <div
            v-for="block in visibleBlocks"
            :key="block.key"
            class="rounded-lg p-4 transition-all"
            :class="blockClass(block.key)"
          >
            <h4 class="text-sm font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
              <span class="text-base">{{ block.icon }}</span>
              {{ $t(`chapterTheory.blocks.${block.i18nKey}`) }}
            </h4>
            <div class="prose dark:prose-invert max-w-none text-sm" v-html="sanitize(formatContent(block.text))"></div>
          </div>
        </template>
      </div>

      <!-- Error -->
      <div v-else class="text-center py-8 text-sm text-gray-500 dark:text-gray-400">
        {{ $t('chapterTheory.noTheory.description') }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import DOMPurify from 'dompurify'

interface Props {
  theory: { theoryId: string; title?: string; style?: string; createdAt?: string; _inlineContent?: any }
  expanded: boolean
  loadContent: (theoryId: string) => Promise<any>
}

const props = defineProps<Props>()
const emit = defineEmits<{ toggle: [] }>()
const { locale } = useI18n()

const content = ref<any>(null)
const contentLoading = ref(false)
const hasLoaded = ref(false)

watch(() => props.expanded, async (isExpanded) => {
  if (isExpanded && !hasLoaded.value) {
    contentLoading.value = true
    try {
      content.value = await props.loadContent(props.theory.theoryId)
    } catch (e) {
      console.error('Failed to load theory content:', e)
      content.value = null
    } finally {
      contentLoading.value = false
      hasLoaded.value = true
    }
  }
}, { immediate: true })

const styleBadgeClass = computed(() => {
  const style = props.theory.style || ''
  const map: Record<string, string> = {
    detailed: 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400',
    adhs: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
    exam_focus: 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400',
    short: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400',
  }
  return map[style] || 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
})

const BLOCK_CONFIG = [
  { key: 'overview', i18nKey: 'overview', icon: 'ℹ️' },
  { key: 'learning_goals', i18nKey: 'learningGoals', icon: '🎯' },
  { key: 'core_concepts', i18nKey: 'coreConcepts', icon: '💡' },
  { key: 'important_terms', i18nKey: 'importantTerms', icon: '📖' },
  { key: 'exam_tips', i18nKey: 'examTips', icon: '⚠️' },
  { key: 'summary', i18nKey: 'summary', icon: '📋' },
]

const visibleBlocks = computed(() => {
  if (!content.value) return []
  return BLOCK_CONFIG.filter(b => content.value[b.key]).map(b => ({ ...b, text: content.value[b.key] }))
})

function blockClass(key: string): string {
  const map: Record<string, string> = {
    exam_tips: 'bg-amber-50 dark:bg-amber-950/20 border border-amber-200/50 dark:border-amber-800/30',
    summary: 'bg-blue-50 dark:bg-blue-950/20 border border-blue-200/50 dark:border-blue-800/30',
    overview: 'bg-slate-50 dark:bg-slate-900/30 border border-slate-200/50 dark:border-slate-700/30',
    learning_goals: 'bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200/50 dark:border-emerald-800/30',
    core_concepts: 'bg-violet-50 dark:bg-violet-950/20 border border-violet-200/50 dark:border-violet-800/30',
    important_terms: 'bg-cyan-50 dark:bg-cyan-950/20 border border-cyan-200/50 dark:border-cyan-800/30',
  }
  return map[key] || 'bg-gray-50 dark:bg-gray-800/50'
}

function formatDate(dateString: string): string {
  try {
    return new Intl.DateTimeFormat(locale.value, { year: 'numeric', month: 'short', day: 'numeric' }).format(new Date(dateString))
  } catch { return dateString }
}

function formatContent(text: string): string {
  if (!text) return ''
  return text
    .replace(/^### (.+)$/gm, '<h4 class="text-base font-semibold mt-4 mb-2">$1</h4>')
    .replace(/^## (.+)$/gm, '<h3 class="text-lg font-semibold mt-5 mb-2">$1</h3>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
}

function sanitize(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'li', 'ul', 'ol', 'h3', 'h4'],
    ALLOWED_ATTR: ['class']
  })
}
</script>

<style scoped>
.prose { line-height: 1.75; }
.prose p { margin-bottom: 0.75rem; }
.prose li { margin-bottom: 0.25rem; }
</style>
