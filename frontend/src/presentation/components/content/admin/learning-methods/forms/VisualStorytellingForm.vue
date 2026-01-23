<!--
  LearningMethod02Form - Interaktive Theorie

  Theoretische Erklärung kombiniert mit eingebetteten Verständnisfragen.
  Der Lernende wird aktiv eingebunden, indem nach jedem Abschnitt
  Rückfragen gestellt werden.

  KI-Nutzung: Mittel - KI generiert Theorie-Blöcke und passende Rückfragen.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <!-- Thema -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Thema *
        </label>
        <input
          v-model="methodData.topic"
          type="text"
          placeholder="z.B. OSI-Modell, Datenbankdesign, Buchhaltungsgrundlagen"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Theorie-Abschnitte mit Fragen -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            Theorie-Abschnitte mit Rückfragen *
          </label>
          <button
            @click="addSection"
            type="button"
            class="text-sm text-[var(--color-primary)] hover:underline"
          >
            + Abschnitt hinzufügen
          </button>
        </div>

        <div v-if="methodData.sections.length === 0" class="text-sm text-[var(--color-text-secondary)] italic mb-3">
          Keine Abschnitte vorhanden. Fügen Sie mindestens einen Theorie-Abschnitt hinzu.
        </div>

        <div v-for="(section, index) in methodData.sections" :key="index" class="mb-4 p-4 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface-secondary)]">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-bold text-[var(--color-primary)]">
              Abschnitt {{ index + 1 }}
            </span>
            <button
              @click="removeSection(index)"
              type="button"
              class="text-sm text-red-500 hover:underline"
            >
              Entfernen
            </button>
          </div>

          <div class="space-y-3">
            <!-- Abschnitt-Titel -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Überschrift
              </label>
              <input
                v-model="section.title"
                type="text"
                placeholder="z.B. Einführung, Kernkonzept, Anwendung..."
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>

            <!-- Theorie-Text -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Theorie-Erklärung *
              </label>
              <textarea
                v-model="section.theory"
                rows="4"
                placeholder="Theoretische Erklärung des Konzepts..."
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Verständnisfrage -->
            <div class="border-t border-[var(--color-border)] pt-3 mt-3">
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Verständnisfrage *
              </label>
              <input
                v-model="section.question"
                type="text"
                placeholder="z.B. Was ist der Hauptzweck von...?"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Erwartete Antwort -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Erwartete Antwort / Schlüsselwörter
              </label>
              <input
                v-model="section.expected_answer"
                type="text"
                placeholder="Schlüsselwörter oder kurze Musterantwort..."
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Abschlussfrage -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Abschlussfrage (optional)
        </label>
        <textarea
          v-model="methodData.final_question"
          rows="2"
          placeholder="Optionale zusammenfassende Frage am Ende..."
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/window.store'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 2

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

interface Section {
  title: string
  theory: string
  question: string
  expected_answer: string
}

// Methoden-spezifische Daten
const methodData = ref({
  topic: '',
  sections: [] as Section[],
  final_question: ''
})

const addSection = () => {
  methodData.value.sections.push({
    title: '',
    theory: '',
    question: '',
    expected_answer: ''
  })
}

const removeSection = (index: number) => {
  methodData.value.sections.splice(index, 1)
}

// Lade existierende Daten im Edit-Mode
onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.topic = existingData.topic || ''
    methodData.value.sections = existingData.sections || []
    methodData.value.final_question = existingData.final_question || ''
  }
})
</script>
