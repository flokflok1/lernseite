<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const props = defineProps<{ courseId: string | null }>()
const { t } = useI18n()
</script>

<template>
  <div class="p-6">
    <div v-if="courseId" class="space-y-4">
      <div class="text-[var(--color-text)]">
        <router-link
          :to="`/course/${courseId}`"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 transition-colors"
        >
          {{ t('panel.programs.tabs.learningPath') }}
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </router-link>
      </div>
    </div>
    <div v-else class="text-center py-12 text-[var(--color-text-secondary)]">
      {{ t('panel.programs.tabs.noCourse') }}
    </div>
  </div>
</template>
