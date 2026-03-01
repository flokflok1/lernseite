<script setup lang="ts">
/**
 * PlanCourseCard — Phase 1 course definition card.
 *
 * Two states:
 * 1. No plan yet: topic input + language select + create button
 * 2. Plan created: shows editable course metadata
 */
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { CourseMeta } from '../../types'
import { languagesApi, type AdminLanguage } from '@/infrastructure/api/clients/panel/admin/i18n/languages.api'

interface Props {
  courseMeta: CourseMeta | null
  isCreating: boolean
  hasFiles: boolean
  fileIds?: string[]
}

const props = defineProps<Props>()
const { t } = useI18n()

const emit = defineEmits<{
  generate: [topic?: string, fileIds?: string[], language?: string]
}>()

const topicInput = ref('')
const selectedLanguage = ref('de')
const availableLanguages = ref<AdminLanguage[]>([])

onMounted(async () => {
  try {
    const all = await languagesApi.getAll()
    availableLanguages.value = all.filter(l => l.active)
  } catch {
    // Fallback: at least show de/en/pl
    availableLanguages.value = []
  }
})

function handleCreate() {
  const topic = topicInput.value.trim()
  emit('generate', topic || undefined, undefined, selectedLanguage.value)
}
</script>

<template>
  <!-- State 1: No plan — Topic Input -->
  <div v-if="!courseMeta" class="flex flex-col items-center gap-4 py-8">
    <div class="text-center">
      <h3 class="text-lg font-semibold text-white mb-1">
        {{ t('aiEditor.planWizard.phase1Title') }}
      </h3>
      <p class="text-sm text-gray-400">
        {{ t('aiEditor.planWizard.topicDescription') }}
      </p>
    </div>

    <div class="w-full max-w-md space-y-3">
      <input
        v-model="topicInput"
        type="text"
        :placeholder="t('aiEditor.planWizard.topicPlaceholder')"
        class="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-sm text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
        :disabled="isCreating"
        @keydown.enter="handleCreate"
      />

      <!-- Language selector -->
      <div class="flex items-center gap-2">
        <label class="text-xs text-gray-400 whitespace-nowrap">{{ t('aiEditor.planWizard.contentLanguage') }}</label>
        <select
          v-model="selectedLanguage"
          class="flex-1 px-2 py-1.5 bg-gray-800 border border-gray-600 rounded text-sm text-white focus:border-blue-500 focus:outline-none"
          :disabled="isCreating"
        >
          <template v-if="availableLanguages.length > 0">
            <option
              v-for="lang in availableLanguages"
              :key="lang.language_code"
              :value="lang.language_code"
            >
              {{ lang.native_name }} ({{ lang.language_code.toUpperCase() }})
            </option>
          </template>
          <template v-else>
            <option value="de">Deutsch (DE)</option>
            <option value="en">English (EN)</option>
            <option value="pl">Polski (PL)</option>
          </template>
        </select>
      </div>
    </div>

    <div class="flex gap-2">
      <button
        class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-500 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        :disabled="isCreating"
        @click="handleCreate"
      >
        {{ isCreating ? t('aiEditor.planWizard.generating') : t('aiEditor.planWizard.createManual') }}
      </button>
      <button
        v-if="hasFiles"
        class="px-4 py-2 text-sm text-gray-300 hover:text-white border border-gray-600 hover:border-gray-500 rounded transition-colors"
        :disabled="isCreating"
        @click="emit('generate', undefined, props.fileIds, selectedLanguage)"
      >
        {{ t('aiEditor.planWizard.createFromFiles') }}
      </button>
    </div>
  </div>

  <!-- State 2: Plan exists — Course Meta Card -->
  <div v-else class="rounded-lg border border-gray-700 bg-gray-800/50 p-4">
    <h3 class="text-lg font-semibold text-white mb-3">
      {{ courseMeta.title }}
    </h3>

    <p v-if="courseMeta.description" class="text-sm text-gray-300 mb-3 leading-relaxed">
      {{ courseMeta.description }}
    </p>

    <div class="grid grid-cols-3 gap-3 text-sm">
      <div>
        <span class="text-gray-500 text-xs block">{{ t('aiEditor.planWizard.targetAudience') }}</span>
        <span class="text-gray-200">{{ courseMeta.target_audience || '—' }}</span>
      </div>
      <div>
        <span class="text-gray-500 text-xs block">{{ t('aiEditor.planWizard.difficulty') }}</span>
        <span class="text-gray-200">{{ courseMeta.difficulty || '—' }}</span>
      </div>
      <div>
        <span class="text-gray-500 text-xs block">{{ t('aiEditor.planWizard.language') }}</span>
        <span class="text-gray-200 uppercase">{{ courseMeta.language || '—' }}</span>
      </div>
    </div>
  </div>
</template>
