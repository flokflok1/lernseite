<!--
  LearningMethod21Form - Zeitlimit-Training

  Prüfungssimulation unter echtem Zeitdruck.
  Trainiert das Arbeiten unter Prüfungsbedingungen.

  KI-Nutzung: Mittel - KI kann zeitbasierte Aufgaben generieren.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <!-- Trainingsthema -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Trainingsthema *
        </label>
        <input
          v-model="methodData.topic"
          type="text"
          placeholder="z.B. AP1 Vorbereitung, Netzwerk-Grundlagen Speed-Test"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Zeitlimit -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Zeitlimit *
        </label>
        <div class="flex items-center gap-4">
          <input
            v-model.number="methodData.time_limit_minutes"
            type="number"
            min="1"
            max="180"
            class="w-24 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            required
          />
          <span class="text-sm text-[var(--color-text-secondary)]">Minuten</span>
        </div>
      </div>

      <!-- Zeit pro Frage (optional) -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Zeit pro Frage (optional)
        </label>
        <div class="flex items-center gap-4">
          <input
            v-model.number="methodData.time_per_question"
            type="number"
            min="0"
            max="600"
            placeholder="0"
            class="w-24 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
          <span class="text-sm text-[var(--color-text-secondary)]">Sekunden (0 = kein Einzellimit)</span>
        </div>
      </div>

      <!-- Fragen -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            Fragen *
          </label>
          <button
            @click="addQuestion"
            type="button"
            class="text-sm text-[var(--color-primary)] hover:underline"
          >
            + Frage hinzufügen
          </button>
        </div>

        <div v-if="methodData.questions.length === 0" class="text-sm text-[var(--color-text-secondary)] italic mb-3">
          Keine Fragen vorhanden.
        </div>

        <div v-for="(question, index) in methodData.questions" :key="index" class="mb-4 p-4 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface-secondary)]">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-bold text-[var(--color-primary)]">
              Frage {{ index + 1 }}
            </span>
            <button
              @click="removeQuestion(index)"
              type="button"
              class="text-sm text-red-500 hover:underline"
            >
              Entfernen
            </button>
          </div>

          <div class="space-y-3">
            <!-- Fragetyp -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Fragetyp *
              </label>
              <select
                v-model="question.type"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              >
                <option value="multiple_choice">Multiple-Choice</option>
                <option value="true_false">Richtig/Falsch</option>
                <option value="short_answer">Kurzantwort</option>
                <option value="number">Zahleneingabe</option>
              </select>
            </div>

            <!-- Fragetext -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Frage *
              </label>
              <textarea
                v-model="question.question"
                rows="2"
                placeholder="Frage eingeben..."
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Multiple-Choice Optionen -->
            <div v-if="question.type === 'multiple_choice'">
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Antwortoptionen (eine pro Zeile)
              </label>
              <textarea
                v-model="question.options"
                rows="4"
                placeholder="Option A
Option B
Option C
Option D"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
              <div class="mt-2">
                <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                  Korrekte Antwort (Index, 0-basiert)
                </label>
                <input
                  v-model.number="question.correct_index"
                  type="number"
                  min="0"
                  class="w-20 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                />
              </div>
            </div>

            <!-- Richtig/Falsch -->
            <div v-if="question.type === 'true_false'">
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Korrekte Antwort
              </label>
              <div class="flex gap-4">
                <label class="flex items-center">
                  <input
                    v-model="question.is_true"
                    type="radio"
                    :value="true"
                    class="mr-2"
                  />
                  <span class="text-sm text-[var(--color-text-primary)]">Richtig</span>
                </label>
                <label class="flex items-center">
                  <input
                    v-model="question.is_true"
                    type="radio"
                    :value="false"
                    class="mr-2"
                  />
                  <span class="text-sm text-[var(--color-text-primary)]">Falsch</span>
                </label>
              </div>
            </div>

            <!-- Kurzantwort / Zahl -->
            <div v-if="question.type === 'short_answer' || question.type === 'number'">
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Korrekte Antwort
              </label>
              <input
                v-model="question.correct_answer"
                :type="question.type === 'number' ? 'number' : 'text'"
                placeholder="Erwartete Antwort..."
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Optionen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Trainings-Optionen
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.shuffle_questions"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Fragen zufällig mischen</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.show_timer"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Timer sichtbar anzeigen</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.auto_submit"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Bei Zeitablauf automatisch abgeben</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.show_remaining"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Verbleibende Fragen anzeigen</span>
          </label>
        </div>
      </div>

      <!-- Warnung -->
      <div class="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
        <p class="text-sm text-red-800 dark:text-red-200">
          <strong>Zeitdruck-Training:</strong> Diese Methode simuliert echten Prüfungsdruck.
          Der Lernende muss innerhalb des Zeitlimits alle Fragen beantworten.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/store/window.store'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 21

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

interface Question {
  type: string
  question: string
  options: string
  correct_index: number
  is_true: boolean
  correct_answer: string
}

// Methoden-spezifische Daten
const methodData = ref({
  topic: '',
  time_limit_minutes: 30,
  time_per_question: 0,
  questions: [] as Question[],
  shuffle_questions: true,
  show_timer: true,
  auto_submit: true,
  show_remaining: true
})

const addQuestion = () => {
  methodData.value.questions.push({
    type: 'multiple_choice',
    question: '',
    options: '',
    correct_index: 0,
    is_true: true,
    correct_answer: ''
  })
}

const removeQuestion = (index: number) => {
  methodData.value.questions.splice(index, 1)
}

// Lade existierende Daten im Edit-Mode
onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.topic = existingData.topic || ''
    methodData.value.time_limit_minutes = existingData.time_limit_minutes || 30
    methodData.value.time_per_question = existingData.time_per_question || 0
    methodData.value.questions = existingData.questions || []
    methodData.value.shuffle_questions = existingData.shuffle_questions ?? true
    methodData.value.show_timer = existingData.show_timer ?? true
    methodData.value.auto_submit = existingData.auto_submit ?? true
    methodData.value.show_remaining = existingData.show_remaining ?? true
  }
})
</script>
