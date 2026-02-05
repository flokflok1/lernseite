<!--
  LearningMethod00Form - Tiefenexploration

  Ermöglicht das Erstellen einer Tiefenexploration mit Konzept, Erklärung und Beispielen.
-->

<template>
  <BaseLearningMethodForm
    :panel="panel"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form: _form }">
      <!-- Concept -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('features.lm00.conceptLabel') }}
        </label>
        <input
          v-model="methodData.concept"
          type="text"
          :placeholder="$t('features.lm00.conceptPlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Explanation -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('features.lm00.explanationLabel') }}
        </label>
        <textarea
          v-model="methodData.explanation"
          rows="6"
          :placeholder="$t('features.lm00.explanationPlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Examples -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('features.lm00.examplesLabel') }}
        </label>
        <textarea
          v-model="methodData.examples"
          rows="4"
          :placeholder="$t('features.lm00.examplesPlaceholder')"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
        <p class="mt-1 text-xs text-[var(--color-text-secondary)]">
          {{ $t('features.lm00.examplesHint') }}
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxPanel } from '@/application/stores/modules/desktop'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 0
const { t } = useI18n()

interface Props {
  panel: LsxPanel
}

const props = defineProps<Props>()

// Methoden-spezifische Daten
const methodData = ref({
  concept: '',
  explanation: '',
  examples: ''
})

// Lade existierende Daten im Edit-Mode
onMounted(() => {
  const existingData = props.panel.payload?.instanceData?.data
  if (existingData) {
    methodData.value.concept = existingData.concept || ''
    methodData.value.explanation = existingData.explanation || ''
    methodData.value.examples = existingData.examples || ''
  }
})
</script>
