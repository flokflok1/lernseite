<script setup lang="ts">
/**
 * PlanChapterList — Phase 2 chapter structure display.
 *
 * Shows generated chapters as a numbered list with titles and descriptions.
 */
import { useI18n } from 'vue-i18n'
import type { ChapterDraft } from '../types'

interface Props {
  chapters: ChapterDraft[]
  isCreating: boolean
}

defineProps<Props>()
const { t } = useI18n()
</script>

<template>
  <!-- Loading State -->
  <div v-if="isCreating && chapters.length === 0" class="flex items-center justify-center py-12">
    <div class="text-center">
      <div class="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-3" />
      <p class="text-sm text-gray-400">{{ t('planWizard.generating') }}</p>
    </div>
  </div>

  <!-- Chapter List -->
  <div v-else class="flex flex-col gap-2">
    <div class="flex items-center justify-between mb-2">
      <h3 class="text-sm font-semibold text-white">
        {{ t('planWizard.phase2Title') }}
      </h3>
      <span class="text-xs text-gray-500">
        {{ t('planWizard.chapterCount', { count: chapters.length }) }}
      </span>
    </div>

    <div
      v-for="(chapter, idx) in chapters"
      :key="chapter.id"
      class="flex gap-3 p-3 rounded-lg border border-gray-700 bg-gray-800/50 hover:border-gray-600 transition-colors"
    >
      <span class="flex-shrink-0 flex items-center justify-center w-7 h-7 rounded-full bg-blue-600/20 text-blue-400 text-xs font-semibold">
        {{ idx + 1 }}
      </span>
      <div class="flex-1 min-w-0">
        <h4 class="text-sm font-medium text-white truncate">{{ chapter.title }}</h4>
        <p v-if="chapter.description" class="text-xs text-gray-400 mt-0.5 line-clamp-2">
          {{ chapter.description }}
        </p>
      </div>
    </div>

    <p v-if="chapters.length === 0" class="text-sm text-gray-500 text-center py-4">
      {{ t('planWizard.noChapters') }}
    </p>
  </div>
</template>
