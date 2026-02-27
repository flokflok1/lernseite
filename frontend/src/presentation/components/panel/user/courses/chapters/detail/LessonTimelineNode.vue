<template>
  <div
    class="lesson-timeline-node relative flex gap-5"
    :class="{ 'cursor-pointer group': status !== 'locked', 'cursor-not-allowed': status === 'locked' }"
    @click="handleClick"
  >
    <!-- Timeline column -->
    <div class="relative flex flex-col items-center" style="width: 44px;">
      <!-- Connector line above (except first) -->
      <div
        v-if="index > 0"
        class="absolute top-0 w-0.5 h-4"
        :class="connectorAboveClass"
      />

      <!-- Dot -->
      <div class="relative z-10 mt-4" :class="dotOuterClass">
        <div class="flex items-center justify-center rounded-full transition-all" :class="dotClasses">
          <svg v-if="status === 'completed'" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
          </svg>
          <svg v-else-if="status === 'current'" class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z" />
          </svg>
          <svg v-else class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
      </div>

      <!-- Connector line below (except last) -->
      <div
        v-if="!isLast"
        class="flex-1 w-0.5 mt-0"
        :class="connectorBelowClass"
      />
    </div>

    <!-- Content card -->
    <div class="flex-1 pt-1.5 pb-3" :class="{ 'pb-0': isLast }">
      <div
        class="rounded-xl border p-4 transition-all duration-200"
        :class="cardClasses"
      >
        <div class="flex items-start justify-between gap-3">
          <!-- Left: title + meta -->
          <div class="min-w-0 flex-1">
            <h4 class="font-semibold text-sm leading-snug" :class="titleClass">
              {{ lesson.title }}
            </h4>
            <div class="mt-2 flex flex-wrap items-center gap-2.5 text-xs text-gray-500 dark:text-gray-400">
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-gray-100 dark:bg-gray-700/50">
                {{ typeEmoji }}
                {{ $t(`lesson.type_${lesson.lesson_type || 'text'}`) }}
              </span>
              <span v-if="lesson.duration_minutes" class="inline-flex items-center gap-1">
                <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ $t('chapter.estimatedDuration', { minutes: lesson.duration_minutes }) }}
              </span>
              <span v-if="progress > 0 && status !== 'completed'" class="text-blue-600 dark:text-blue-400 font-semibold">
                {{ progress }}%
              </span>
            </div>
          </div>

          <!-- Right: status + arrow -->
          <div class="flex items-center gap-2 flex-shrink-0">
            <span :class="['text-xs font-semibold px-2.5 py-1 rounded-full', badgeClasses]">
              {{ statusLabel }}
            </span>
            <svg
              v-if="status !== 'locked'"
              class="w-5 h-5 text-gray-300 dark:text-gray-600 transition-transform group-hover:translate-x-1 group-hover:text-blue-400"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface Props {
  lesson: any
  index: number
  status: 'completed' | 'current' | 'locked'
  progress: number
  isLast: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{ select: [lesson: any, index: number] }>()
const { t } = useI18n()

const dotOuterClass = computed(() => {
  if (props.status === 'current') return 'animate-pulse'
  return ''
})

const dotClasses = computed(() => {
  switch (props.status) {
    case 'completed': return 'h-10 w-10 bg-green-500 dark:bg-green-600 text-white shadow-md shadow-green-500/30'
    case 'current': return 'h-10 w-10 bg-blue-500 dark:bg-blue-600 text-white ring-[3px] ring-blue-300/50 dark:ring-blue-400/30 shadow-lg shadow-blue-500/30'
    default: return 'h-10 w-10 bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500'
  }
})

const connectorAboveClass = computed(() => {
  if (props.status === 'completed') return 'bg-green-400 dark:bg-green-500'
  if (props.status === 'current') return 'bg-gradient-to-b from-green-400 to-blue-400'
  return 'bg-gray-200 dark:bg-gray-700'
})

const connectorBelowClass = computed(() => {
  if (props.status === 'completed') return 'bg-green-400 dark:bg-green-500'
  return 'bg-gray-200 dark:bg-gray-700'
})

const cardClasses = computed(() => {
  switch (props.status) {
    case 'completed': return 'border-green-200 dark:border-green-800/50 bg-green-50/50 dark:bg-green-900/10 hover:bg-green-50 dark:hover:bg-green-900/20'
    case 'current': return 'border-blue-300 dark:border-blue-700/50 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/15 shadow-md hover:shadow-lg'
    default: return 'border-gray-200 dark:border-gray-700/50 bg-gray-50/50 dark:bg-gray-800/30 opacity-60'
  }
})

const titleClass = computed(() => {
  if (props.status === 'locked') return 'text-gray-400 dark:text-gray-500'
  return 'text-gray-900 dark:text-white'
})

const badgeClasses = computed(() => {
  switch (props.status) {
    case 'completed': return 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-400'
    case 'current': return 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400'
    default: return 'bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-500'
  }
})

const statusLabel = computed(() => {
  switch (props.status) {
    case 'completed': return t('lessonTimeline.statusCompleted')
    case 'current': return t('lessonTimeline.statusCurrent')
    default: return t('lessonTimeline.statusLocked')
  }
})

const typeEmoji = computed(() => {
  const map: Record<string, string> = { text: '📝', video: '🎬', quiz: '❓', ai: '🤖', interactive: '🎮', mixed: '🔀' }
  return map[props.lesson.lesson_type || 'text'] || '📄'
})

function handleClick() {
  if (props.status !== 'locked') emit('select', props.lesson, props.index)
}
</script>
