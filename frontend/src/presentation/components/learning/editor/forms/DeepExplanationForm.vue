<!--
  LearningMethod00Form - Tiefenexploration

  Ermöglicht das Erstellen einer Tiefenexploration mit Konzept, Erklärung und Beispielen.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form: _form }">
      <!-- Konzept -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Konzept *
        </label>
        <input
          v-model="methodData.concept"
          type="text"
          placeholder="z.B. Photosynthese, Quantenmechanik, etc."
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Erklärung -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Erklärung *
        </label>
        <textarea
          v-model="methodData.explanation"
          rows="6"
          placeholder="Detaillierte Erklärung des Konzepts..."
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Beispiele -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Beispiele
        </label>
        <textarea
          v-model="methodData.examples"
          rows="4"
          placeholder="Praktische Beispiele (ein Beispiel pro Zeile oder durch Kommas getrennt)..."
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
        <p class="mt-1 text-xs text-[var(--color-text-secondary)]">
          Optional: Geben Sie konkrete Beispiele an, um das Konzept zu veranschaulichen
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/window.store'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 0

interface Props {
  window: LsxWindow
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
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.concept = existingData.concept || ''
    methodData.value.explanation = existingData.explanation || ''
    methodData.value.examples = existingData.examples || ''
  }
})
</script>
