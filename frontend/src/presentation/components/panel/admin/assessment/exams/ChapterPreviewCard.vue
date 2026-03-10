<!--
  ChapterPreviewCard — Displays a single chapter preview within
  the exam course generator plan view. Shows topic, question count,
  points, child topics, and learning method badges.
-->

<template>
  <div class="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-4">
    <div class="flex items-center justify-between">
      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-2">
          <span
            v-if="chapter.curriculum_position_code"
            class="text-xs font-mono px-1.5 py-0.5 rounded bg-[var(--color-info-bg,#eff6ff)] text-[var(--color-info-text,#2563eb)]"
          >
            {{ chapter.curriculum_position_code }}
          </span>
          <span v-else class="text-xs font-mono text-[var(--color-text-secondary)] w-6 shrink-0">
            {{ index + 1 }}
          </span>
          <h4 class="font-semibold text-[var(--color-text-primary)] truncate">
            {{ title }}
          </h4>
        </div>
        <p class="text-sm text-[var(--color-text-secondary)] mt-1 ml-8">
          {{ chapter.question_count }} {{ t('panel.examCourseGenerator.questions') }},
          {{ Math.round(chapter.point_weight) }} {{ t('panel.examCourseGenerator.points') }}
        </p>
        <!-- Coverage info -->
        <div v-if="chapter.objectives_total" class="mt-1 ml-8 flex items-center gap-2">
          <span class="text-xs px-2 py-0.5 rounded" :class="coverageBadgeClass">
            {{ chapter.objectives_with_questions }}/{{ chapter.objectives_total }}
            {{ t('panel.examCourseGenerator.objectivesCovered') }}
          </span>
          <span
            v-if="(chapter.objectives_ai_only ?? 0) > 0"
            class="text-xs px-2 py-0.5 rounded bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400"
          >
            {{ chapter.objectives_ai_only }} {{ t('panel.examCourseGenerator.aiOnly') }}
          </span>
        </div>
        <!-- Exam relevance -->
        <div v-if="chapter.relevance_score > 0" class="mt-1 ml-8 flex items-center gap-2">
          <span class="text-xs px-2 py-0.5 rounded" :class="relevanceBadgeClass">
            {{ Math.round(chapter.exam_appearance_rate * 100) }}%
            {{ t('panel.examCourseGenerator.examAppearance') }}
          </span>
          <span v-if="chapter.relevance_trend" class="text-xs" :class="trendClass">
            {{ trendIcon }} {{ t(`panel.examCourseGenerator.trend_${chapter.relevance_trend}`) }}
          </span>
        </div>
        <div v-if="chapter.child_topics?.length" class="mt-2 ml-8 flex flex-wrap gap-1">
          <span
            v-for="child in chapter.child_topics"
            :key="child"
            class="text-xs px-2 py-0.5 rounded bg-[var(--color-primary-bg,#ede9fe)] text-[var(--color-primary-text,#6d28d9)]"
          >
            {{ formatTopic(child) }}
          </span>
        </div>
      </div>
      <div class="text-right text-sm text-[var(--color-text-secondary)] shrink-0 ml-4">
        <div class="flex gap-1 flex-wrap justify-end">
          <span
            v-for="lm in chapter.lm_types"
            :key="lm"
            class="px-1.5 py-0.5 text-xs rounded bg-[var(--color-primary-bg,#ede9fe)] text-[var(--color-primary-text,#6d28d9)]"
          >
            LM{{ lm }}
          </span>
        </div>
        <span class="text-xs text-[var(--color-text-secondary)] mt-1 block">
          {{ chapter.lm_types.length }} {{ t('panel.examCourseGenerator.lmCount') }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChapterPreview } from '@/infrastructure/api/clients/panel/admin/exams/course-generator.api'

const ACRONYMS = new Set([
  'sql', 'erm', 'csv', 'xml', 'json', 'html', 'dhcp',
  'raid', 'itil', 'vpn', 'ipv4', 'osi', 'dsgvo', 'wlan',
  'it', 'ip', 'css', 'http', 'https', 'api', 'dns', 'tcp', 'udp',
])

interface Props {
  chapter: ChapterPreview
  index: number
}

const props = defineProps<Props>()
const { t, locale } = useI18n()

function formatTopic(topic: string): string {
  return topic
    .replace(/_/g, ' ')
    .split(' ')
    .map(word => {
      if (ACRONYMS.has(word.toLowerCase())) return word.toUpperCase()
      return word.charAt(0).toUpperCase() + word.slice(1)
    })
    .join(' ')
}

const coverageBadgeClass = computed(() => {
  if (!props.chapter.objectives_total) return ''
  const ratio = (props.chapter.objectives_with_questions || 0) / props.chapter.objectives_total
  if (ratio >= 0.8) return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
  if (ratio >= 0.5) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
  return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
})

const title = computed(() => {
  if (props.chapter.parent_label) {
    const label = props.chapter.parent_label[locale.value]
      || props.chapter.parent_label['de']
      || props.chapter.parent_label['en']
    if (label) return label
  }
  return formatTopic(props.chapter.topic)
})

const relevanceBadgeClass = computed(() => {
  const rate = props.chapter.exam_appearance_rate ?? 0
  if (rate >= 0.7) return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
  if (rate >= 0.4) return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400'
  return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
})

const trendIcon = computed(() => {
  const t = props.chapter.relevance_trend
  if (t === 'rising') return '\u2191'
  if (t === 'declining') return '\u2193'
  return '\u2192'
})

const trendClass = computed(() => {
  const t = props.chapter.relevance_trend
  if (t === 'rising') return 'text-red-600 dark:text-red-400 font-medium'
  if (t === 'declining') return 'text-green-600 dark:text-green-400'
  return 'text-[var(--color-text-secondary)]'
})
</script>
