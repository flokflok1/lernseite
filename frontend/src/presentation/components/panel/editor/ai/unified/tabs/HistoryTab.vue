<script setup lang="ts">
/**
 * HistoryTab — Generation history with filtering
 */
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useGenerationHistory } from '../composables'

interface Props {
  courseId: string
}

const props = defineProps<Props>()
const { t } = useI18n()

const history = useGenerationHistory()

onMounted(() => {
  if (props.courseId) {
    history.loadHistory(props.courseId)
  }
})

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString()
}
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="p-4 border-b border-gray-700 flex items-center justify-between">
      <h3 class="text-sm font-semibold text-white">{{ t('aiEditor.history.title') }}</h3>
      <span class="text-xs text-gray-500">
        {{ history.totalTokens.value.toLocaleString() }} {{ t('aiEditor.history.totalTokens') }}
      </span>
    </div>

    <!-- Filter -->
    <div v-if="history.uniqueSkills.value.length > 1" class="p-4 border-b border-gray-700">
      <div class="flex gap-1.5 flex-wrap">
        <button
          class="px-2.5 py-1 rounded-full text-xs"
          :class="!history.filterSkill.value ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400'"
          @click="history.setFilter(null)"
        >
          {{ t('aiEditor.history.all') }}
        </button>
        <button
          v-for="skill in history.uniqueSkills.value"
          :key="skill"
          class="px-2.5 py-1 rounded-full text-xs"
          :class="history.filterSkill.value === skill ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400'"
          @click="history.setFilter(skill)"
        >
          {{ skill }}
        </button>
      </div>
    </div>

    <!-- Entries -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="history.isLoading.value" class="p-8 text-center text-gray-500 text-sm animate-pulse">
        {{ t('common.loading') }}
      </div>
      <div v-else-if="history.filteredEntries.value.length === 0" class="p-8 text-center text-gray-500 text-sm">
        {{ t('aiEditor.history.empty') }}
      </div>
      <div v-else class="divide-y divide-gray-800">
        <div
          v-for="entry in history.filteredEntries.value"
          :key="entry.generation_id"
          class="p-4 hover:bg-gray-800/30 transition-colors"
        >
          <div class="flex items-center justify-between mb-1">
            <span class="text-sm text-white font-medium">{{ entry.skill_code }}</span>
            <span class="text-[10px] px-1.5 py-0.5 rounded" :class="{
              'bg-green-900/50 text-green-400': entry.status === 'completed',
              'bg-red-900/50 text-red-400': entry.status === 'failed',
              'bg-blue-900/50 text-blue-400': entry.status === 'running',
            }">
              {{ entry.status }}
            </span>
          </div>
          <div class="flex items-center gap-3 text-xs text-gray-500">
            <span>{{ entry.model_name }}</span>
            <span>{{ (entry.tokens_input + entry.tokens_output).toLocaleString() }} tokens</span>
            <span>{{ formatDate(entry.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
