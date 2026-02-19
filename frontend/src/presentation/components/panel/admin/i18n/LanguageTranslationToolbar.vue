<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 space-y-4">
    <!-- Seed Reference Data -->
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-sm font-medium text-gray-900 dark:text-white">
          {{ $t('panel.languages.seed.button') }}
        </h3>
        <p class="text-xs text-gray-500 dark:text-gray-400">
          {{ $t('panel.languages.seed.hint') }}
        </p>
      </div>
      <button
        @click="handleSeed"
        :disabled="seedImport.importing.value"
        class="px-3 py-1.5 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 transition-colors"
      >
        <template v-if="seedImport.importing.value">
          {{ $t('panel.languages.seed.importing', { lang: seedImport.currentLang.value }) }}
        </template>
        <template v-else>
          {{ $t('panel.languages.seed.button') }}
        </template>
      </button>
    </div>

    <!-- Seed Results -->
    <div v-if="seedImport.importResults.value.length > 0" class="text-xs text-green-600 dark:text-green-400 space-y-1">
      <p v-for="r in seedImport.importResults.value" :key="r.lang">
        {{ $t('panel.languages.seed.success', { count: r.count, lang: r.lang }) }}
      </p>
      <p class="font-medium">{{ $t('panel.languages.seed.complete') }}</p>
    </div>

    <!-- Seed Error -->
    <p v-if="seedImport.error.value" class="text-xs text-red-600 dark:text-red-400">
      {{ seedImport.error.value }}
    </p>

    <hr class="border-gray-200 dark:border-gray-700" />

    <!-- AI Translate -->
    <div class="space-y-3">
      <h3 class="text-sm font-medium text-gray-900 dark:text-white">
        {{ $t('panel.languages.translate.button') }}
      </h3>

      <div class="flex items-end gap-3">
        <!-- Source Language -->
        <div class="flex-1">
          <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">
            {{ $t('panel.languages.translate.sourceLanguage') }}
          </label>
          <select
            v-model="sourceLanguage"
            class="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option v-for="lang in languages" :key="lang.language_code" :value="lang.language_code">
              {{ lang.language_name }} ({{ lang.language_code }})
            </option>
          </select>
        </div>

        <!-- Arrow -->
        <span class="text-gray-400 pb-1.5">&rarr;</span>

        <!-- Target Language -->
        <div class="flex-1">
          <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">
            {{ $t('panel.languages.translate.targetLanguage') }}
          </label>
          <select
            v-model="targetLanguage"
            class="w-full px-2 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option v-for="lang in targetOptions" :key="lang.language_code" :value="lang.language_code">
              {{ lang.language_name }} ({{ lang.language_code }})
            </option>
          </select>
        </div>

        <!-- Start Button -->
        <button
          @click="handleTranslate"
          :disabled="bulk.translating.value || !targetLanguage"
          class="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors whitespace-nowrap"
        >
          {{ $t('panel.languages.translate.start') }}
        </button>
      </div>

      <!-- Progress -->
      <div v-if="bulk.translating.value || bulk.status.value === 'completed'" class="space-y-2">
        <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
          <div
            class="h-2.5 rounded-full transition-all duration-300"
            :class="bulk.status.value === 'completed' ? 'bg-green-500' : bulk.status.value === 'failed' ? 'bg-red-500' : 'bg-blue-500'"
            :style="{ width: `${bulk.progressPercent.value}%` }"
          />
        </div>
        <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400">
          <span>
            {{ $t('panel.languages.translate.translatedCount', { translated: bulk.translated.value, total: bulk.total.value }) }}
          </span>
          <span v-if="bulk.failed.value > 0" class="text-red-500">
            {{ $t('panel.languages.translate.failedCount', { count: bulk.failed.value }) }}
          </span>
          <span v-if="bulk.status.value === 'completed'" class="text-green-600 font-medium">
            {{ $t('panel.languages.translate.complete') }}
          </span>
          <span v-else-if="bulk.status.value === 'failed'" class="text-red-600 font-medium">
            {{ $t('panel.languages.translate.error') }}
          </span>
          <span v-else>
            {{ $t('panel.languages.translate.progress', { percent: bulk.progressPercent.value }) }}
          </span>
        </div>
      </div>

      <!-- Translation Error -->
      <p v-if="bulk.error.value" class="text-xs text-red-600 dark:text-red-400">
        {{ bulk.error.value }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * LanguageTranslationToolbar
 *
 * Provides seed + AI translate actions for the languages admin page.
 * Extracted as sub-component to keep PanelLanguagesPage under 500 lines.
 */
import { ref, computed, watch } from 'vue'
import type { AdminLanguage } from '@/infrastructure/api/clients/panel/admin'
import { useLocaleImport } from './composables/useLocaleImport'
import { useBulkTranslate } from './composables/useBulkTranslate'

const props = defineProps<{
  languages: AdminLanguage[]
}>()

const emit = defineEmits<{
  refreshLanguages: []
}>()

const seedImport = useLocaleImport()
const bulk = useBulkTranslate()

const sourceLanguage = ref('')
const targetLanguage = ref('')

// Default source to primary language (de), targets exclude source
watch(() => props.languages, (langs) => {
  if (langs.length > 0 && !sourceLanguage.value) {
    const primary = langs.find(l => l.is_primary)
    sourceLanguage.value = primary?.language_code ?? langs[0].language_code
  }
}, { immediate: true })

const targetOptions = computed(() =>
  props.languages.filter(l => l.language_code !== sourceLanguage.value)
)

async function handleSeed() {
  await seedImport.seedAll()
  emit('refreshLanguages')
}

async function handleTranslate() {
  if (!targetLanguage.value) return
  await bulk.startTranslation(sourceLanguage.value, targetLanguage.value)
  emit('refreshLanguages')
}
</script>
