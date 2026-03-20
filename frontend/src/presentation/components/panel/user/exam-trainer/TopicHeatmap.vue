<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { TopicStat } from '@/infrastructure/api/clients/panel/user/exams'

interface Props {
  topics: TopicStat[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'select-topic': [topic: string]
}>()

const { t } = useI18n()

interface TopicDisplay extends TopicStat {
  correctRate: number
  level: 'strong' | 'medium' | 'weak' | 'none'
}

const topicDisplays = computed<TopicDisplay[]>(() => {
  return props.topics.map((topic) => {
    const correctRate = topic.attempts > 0
      ? Math.round((topic.correct_count / topic.attempts) * 100)
      : -1
    let level: TopicDisplay['level'] = 'none'
    if (topic.attempts > 0) {
      if (correctRate > 70) level = 'strong'
      else if (correctRate >= 30) level = 'medium'
      else level = 'weak'
    }
    return { ...topic, correctRate, level }
  })
})

const getLevelClasses = (level: TopicDisplay['level']): string => {
  switch (level) {
    case 'strong':
      return 'bg-emerald-500/10 border-emerald-500/30 hover:border-emerald-500/50'
    case 'medium':
      return 'bg-amber-500/10 border-amber-500/30 hover:border-amber-500/50'
    case 'weak':
      return 'bg-red-500/10 border-red-500/30 hover:border-red-500/50'
    default:
      return 'bg-[var(--color-surface)] border-[var(--color-border)] hover:border-[var(--color-text-secondary)]'
  }
}

const getLevelDotClasses = (level: TopicDisplay['level']): string => {
  switch (level) {
    case 'strong': return 'bg-emerald-500'
    case 'medium': return 'bg-amber-500'
    case 'weak': return 'bg-red-500'
    default: return 'bg-gray-400'
  }
}
</script>

<template>
  <div>
    <!-- Legend -->
    <div class="flex flex-wrap gap-4 mb-4 text-sm">
      <span class="flex items-center gap-1.5">
        <span class="w-3 h-3 rounded-full bg-emerald-500" />
        {{ t('panel.examTrainer.strong') }} (&gt;70%)
      </span>
      <span class="flex items-center gap-1.5">
        <span class="w-3 h-3 rounded-full bg-amber-500" />
        {{ t('panel.examTrainer.medium') }} (30-70%)
      </span>
      <span class="flex items-center gap-1.5">
        <span class="w-3 h-3 rounded-full bg-red-500" />
        {{ t('panel.examTrainer.weak') }} (&lt;30%)
      </span>
      <span class="flex items-center gap-1.5">
        <span class="w-3 h-3 rounded-full bg-gray-400" />
        {{ t('panel.examTrainer.notAttempted') }}
      </span>
    </div>

    <!-- Topic Grid -->
    <div
      v-if="topicDisplays.length > 0"
      class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3"
    >
      <button
        v-for="topic in topicDisplays"
        :key="topic.topic"
        class="text-left p-4 rounded-lg border-2 transition-all cursor-pointer"
        :class="getLevelClasses(topic.level)"
        @click="emit('select-topic', topic.topic)"
      >
        <div class="flex items-start gap-2">
          <span class="mt-1 w-2.5 h-2.5 rounded-full shrink-0" :class="getLevelDotClasses(topic.level)" />
          <div class="min-w-0 flex-1">
            <p class="font-medium text-[var(--color-text)] truncate">{{ topic.topic }}</p>
            <div class="mt-1 text-xs text-[var(--color-text-secondary)]">
              <span v-if="topic.attempts > 0">
                {{ t('panel.examTrainer.correctRate', { rate: topic.correctRate }) }}
                &middot;
                {{ t('panel.examTrainer.attempts', { count: topic.attempts }) }}
              </span>
              <span v-else>
                {{ t('panel.examTrainer.notAttempted') }}
              </span>
              <span class="block mt-0.5">
                {{ t('panel.examTrainer.questions', { count: topic.question_count }) }}
              </span>
            </div>
          </div>
        </div>
      </button>
    </div>

    <p v-else class="text-[var(--color-text-secondary)] text-center py-8">
      {{ t('panel.examTrainer.noTopics') }}
    </p>
  </div>
</template>
