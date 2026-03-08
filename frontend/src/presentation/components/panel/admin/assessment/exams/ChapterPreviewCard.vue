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
          <span class="text-xs font-mono text-[var(--color-text-secondary)] w-6 shrink-0">
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

const title = computed(() => {
  if (props.chapter.parent_label) {
    const label = props.chapter.parent_label[locale.value]
      || props.chapter.parent_label['de']
      || props.chapter.parent_label['en']
    if (label) return label
  }
  return formatTopic(props.chapter.topic)
})
</script>
