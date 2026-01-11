<template>
  <Card :title="$t('widgets.coursesProgress.title')">
    <div class="space-y-4">
      <!-- Stats Grid -->
      <div class="grid grid-cols-2 gap-4">
        <div class="text-center p-3 bg-blue-50 rounded-lg">
          <p class="text-sm text-gray-600 mb-1">{{ $t('widgets.coursesProgress.coursesStarted') }}</p>
          <p class="text-3xl font-bold text-blue-600">{{ stats.started }}</p>
        </div>

        <div class="text-center p-3 bg-green-50 rounded-lg">
          <p class="text-sm text-gray-600 mb-1">{{ $t('widgets.coursesProgress.completed') }}</p>
          <p class="text-3xl font-bold text-green-600">{{ stats.completed }}</p>
        </div>
      </div>

      <!-- Average Progress -->
      <div class="pt-3 border-t border-gray-200">
        <div class="flex items-center justify-between text-sm text-gray-600 mb-2">
          <span>{{ $t('widgets.coursesProgress.averageProgress') }}</span>
          <span class="font-semibold">{{ Math.round(stats.avgProgress) }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-3">
          <div
            class="bg-gradient-to-r from-primary-500 to-primary-600 h-3 rounded-full transition-all"
            :style="{ width: `${stats.avgProgress}%` }"
          ></div>
        </div>
      </div>

      <!-- Total Lessons -->
      <div v-if="stats.totalLessons > 0" class="pt-3 border-t border-gray-200">
        <p class="text-sm text-gray-600 mb-1">{{ $t('widgets.coursesProgress.lessonsCompleted') }}</p>
        <p class="text-lg font-semibold">
          {{ stats.lessonsCompleted }} / {{ stats.totalLessons }}
        </p>
      </div>

      <!-- Motivational Message -->
      <div v-if="stats.started > 0" class="bg-primary-50 border border-primary-200 p-3 rounded">
        <p class="text-sm text-primary-800">
          {{ motivationalMessage }}
        </p>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Card from '@/components/base/Card.vue'
import type { BaseWidgetProps } from '@/types/widgets'

const { t } = useI18n()

// ============================================================================
// Props
// ============================================================================

interface Props extends BaseWidgetProps {
  dataContext: any
}

const props = defineProps<Props>()

// ============================================================================
// Computed
// ============================================================================

const courses = computed(() => props.dataContext.enrolledCourses || [])

const stats = computed(() => {
  const coursesArray = courses.value

  if (coursesArray.length === 0) {
    return {
      started: 0,
      completed: 0,
      avgProgress: 0,
      totalLessons: 0,
      lessonsCompleted: 0
    }
  }

  const started = coursesArray.length
  const completed = coursesArray.filter((c: any) => c.is_completed).length
  const totalProgress = coursesArray.reduce((sum: number, c: any) => sum + (c.progress || 0), 0)
  const avgProgress = started > 0 ? totalProgress / started : 0

  const totalLessons = coursesArray.reduce((sum: number, c: any) => sum + (c.total_lessons || 0), 0)
  const lessonsCompleted = coursesArray.reduce((sum: number, c: any) => sum + (c.lessons_completed || 0), 0)

  return {
    started,
    completed,
    avgProgress,
    totalLessons,
    lessonsCompleted
  }
})

const motivationalMessage = computed(() => {
  const { avgProgress, completed, started } = stats.value

  if (completed === started) {
    return `🎉 ${t('widgets.coursesProgress.motivation.allCompleted')}`
  } else if (avgProgress >= 75) {
    return `💪 ${t('widgets.coursesProgress.motivation.veryGood')}`
  } else if (avgProgress >= 50) {
    return `👍 ${t('widgets.coursesProgress.motivation.halfway')}`
  } else if (avgProgress >= 25) {
    return `🚀 ${t('widgets.coursesProgress.motivation.keepGoing')}`
  } else {
    return `✨ ${t('widgets.coursesProgress.motivation.goodStart')}`
  }
})
</script>
