<template>
  <div class="theory-accordion px-6 pt-4 pb-4">
    <div class="max-w-5xl mx-auto">
      <!-- Section Header -->
      <div class="mb-3">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
          {{ $t('chapterTheory.sheetsTitle') }}
          <span
            v-if="theories.length > 0"
            class="text-sm font-normal text-gray-500 dark:text-gray-400"
          >
            ({{ theories.length }})
          </span>
        </h2>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-10">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400 mb-4"></div>
        <p class="text-gray-600 dark:text-gray-400">{{ $t('chapterTheory.loading.generating') }}</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="theories.length === 0" class="text-center py-10">
        <div class="mb-4">
          <svg class="w-16 h-16 mx-auto text-gray-400 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          {{ $t('chapterTheory.noTheory.title') }}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ $t('chapterTheory.noTheory.emptyHint') }}
        </p>
      </div>

      <!-- Accordion list -->
      <div v-else class="space-y-3">
        <TheoryAccordionItem
          v-for="theory in theories"
          :key="theory.theoryId"
          :theory="theory"
          :expanded="expandedId === theory.theoryId"
          :load-content="loadContent"
          @toggle="toggleItem(theory.theoryId)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import TheoryAccordionItem from './TheoryAccordionItem.vue'

interface Props {
  theories: any[]
  loading: boolean
  loadContent: (theoryId: string) => Promise<any>
}

defineProps<Props>()

const expandedId = ref<string | null>(null)

function toggleItem(theoryId: string) {
  expandedId.value = expandedId.value === theoryId ? null : theoryId
}
</script>
