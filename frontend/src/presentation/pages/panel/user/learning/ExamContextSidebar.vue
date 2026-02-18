<script setup lang="ts">
/**
 * ExamContextSidebar Component
 *
 * Displays the detected exam context information in the sidebar:
 * - Profession, exam level, region, confidence
 * - Weak topics with color-coded scores
 * - Strong topics with color-coded scores
 */

import type { ExamContext } from '@/application/services/api/learning'

interface Props {
  examContext: ExamContext | null
}

defineProps<Props>()

function getTopicColor(score: number): string {
  if (score < 50) return 'text-red-600'
  if (score < 70) return 'text-yellow-600'
  if (score < 85) return 'text-blue-600'
  return 'text-green-600'
}
</script>

<template>
  <div class="lg:col-span-1">
    <!-- Detected Context -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-lg font-semibold mb-4">{{ $t('examSimulation.detectedContext') }}</h2>

      <div v-if="examContext" class="space-y-3">
        <div v-if="examContext.profession">
          <span class="text-gray-500 text-sm">{{ $t('examSimulation.profession') }}</span>
          <p class="font-medium">{{ examContext.profession }}</p>
        </div>
        <div v-if="examContext.exam_level">
          <span class="text-gray-500 text-sm">{{ $t('examSimulation.examLevel') }}</span>
          <p class="font-medium">{{ examContext.exam_level }}</p>
        </div>
        <div v-if="examContext.region">
          <span class="text-gray-500 text-sm">{{ $t('examSimulation.region') }}</span>
          <p class="font-medium">{{ examContext.region }}</p>
        </div>
        <div class="pt-2 border-t">
          <span class="text-gray-500 text-sm">{{ $t('examSimulation.confidence') }}</span>
          <div class="flex items-center gap-2 mt-1">
            <div class="flex-1 bg-gray-200 rounded-full h-2">
              <div
                class="bg-blue-600 h-2 rounded-full"
                :style="{ width: `${(examContext.confidence || 0) * 100}%` }"
              ></div>
            </div>
            <span class="text-sm font-medium">
              {{ Math.round((examContext.confidence || 0) * 100) }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Weak Topics -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-lg font-semibold mb-4">{{ $t('examSimulation.weakTopics') }}</h2>
      <div v-if="examContext?.weak_topics?.length" class="space-y-2">
        <div
          v-for="topic in examContext.weak_topics"
          :key="topic.topic"
          class="flex items-center justify-between"
        >
          <span class="text-sm">{{ topic.topic }}</span>
          <span :class="['text-sm font-medium', getTopicColor(topic.score)]">
            {{ Math.round(topic.score) }}%
          </span>
        </div>
      </div>
      <p v-else class="text-gray-500 text-sm">{{ $t('examSimulation.noDataAvailable') }}</p>
    </div>

    <!-- Strong Topics -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold mb-4">{{ $t('examSimulation.strongTopics') }}</h2>
      <div v-if="examContext?.strong_topics?.length" class="space-y-2">
        <div
          v-for="topic in examContext.strong_topics"
          :key="topic.topic"
          class="flex items-center justify-between"
        >
          <span class="text-sm">{{ topic.topic }}</span>
          <span :class="['text-sm font-medium', getTopicColor(topic.score)]">
            {{ Math.round(topic.score) }}%
          </span>
        </div>
      </div>
      <p v-else class="text-gray-500 text-sm">{{ $t('examSimulation.noDataAvailable') }}</p>
    </div>
  </div>
</template>
