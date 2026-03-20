<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { TopicFrequency } from '@/infrastructure/api/clients/panel/user/exams'
import { trainerGetTopicFrequency } from '@/infrastructure/api/clients/panel/user/exams'

const { t, locale } = useI18n()

const topicLabel = (topic: TopicFrequency): string => {
  if (topic.display_name) {
    return topic.display_name[locale.value] || topic.display_name.de || topic.topic
  }
  return topic.topic
}

const topics = ref<TopicFrequency[]>([])
const totalExams = ref(0)
const isLoading = ref(true)

const topTopics = computed(() => topics.value.slice(0, 20))

const barColor = (pct: number): string => {
  if (pct >= 60) return 'bg-red-500'
  if (pct >= 40) return 'bg-amber-500'
  if (pct >= 20) return 'bg-blue-500'
  return 'bg-gray-400'
}

const barLabel = (pct: number): string => {
  if (pct >= 60) return t('panel.examTrainer.prognosis.veryLikely')
  if (pct >= 40) return t('panel.examTrainer.prognosis.likely')
  if (pct >= 20) return t('panel.examTrainer.prognosis.possible')
  return t('panel.examTrainer.prognosis.rare')
}

onMounted(async () => {
  try {
    const data = await trainerGetTopicFrequency()
    topics.value = data.topics
    totalExams.value = data.total_exams
  } catch {
    // non-critical
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div>
    <div v-if="isLoading" class="flex justify-center py-6">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" />
    </div>

    <div v-else-if="topTopics.length === 0" class="text-center py-6 text-[var(--color-text-secondary)]">
      {{ t('panel.examTrainer.prognosis.noData') }}
    </div>

    <div v-else>
      <!-- Legend -->
      <div class="flex flex-wrap gap-4 mb-4 text-sm text-[var(--color-text-secondary)]">
        <span>{{ t('panel.examTrainer.prognosis.basedOn', { count: totalExams }) }}</span>
        <span class="flex items-center gap-1.5">
          <span class="w-3 h-3 rounded-full bg-red-500" />
          {{ t('panel.examTrainer.prognosis.veryLikely') }} (&gt;60%)
        </span>
        <span class="flex items-center gap-1.5">
          <span class="w-3 h-3 rounded-full bg-amber-500" />
          {{ t('panel.examTrainer.prognosis.likely') }} (40-60%)
        </span>
        <span class="flex items-center gap-1.5">
          <span class="w-3 h-3 rounded-full bg-blue-500" />
          {{ t('panel.examTrainer.prognosis.possible') }} (20-40%)
        </span>
      </div>

      <!-- Topic bars -->
      <div class="space-y-2">
        <div
          v-for="topic in topTopics"
          :key="topic.topic"
          class="flex items-center gap-3"
        >
          <div class="w-36 text-sm font-medium text-[var(--color-text)] truncate" :title="topicLabel(topic)">
            {{ topicLabel(topic) }}
          </div>
          <div class="flex-1 h-6 bg-[var(--color-background)] rounded-full overflow-hidden relative">
            <div
              :class="['h-full rounded-full transition-all', barColor(topic.frequency_pct)]"
              :style="{ width: topic.frequency_pct + '%' }"
            />
            <span class="absolute inset-0 flex items-center justify-end pr-2 text-xs font-medium text-[var(--color-text)]">
              {{ topic.frequency_pct }}%
            </span>
          </div>
          <div class="w-20 text-xs text-[var(--color-text-secondary)] text-right">
            {{ topic.question_count }} {{ t('panel.examTrainer.prognosis.questions') }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
