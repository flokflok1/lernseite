<!--
  LearningMethod18Form - Freitext-Prüfung

  KI-bewertete offene Fragen, bei denen Lernende ausführliche
  Textantworten geben und KI-basiertes Feedback erhalten.

  KI-Nutzung: Hoch - KI bewertet Freitext-Antworten und gibt Feedback.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <!-- Prüfungsthema -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Prüfungsthema *
        </label>
        <input
          v-model="methodData.exam_topic"
          type="text"
          placeholder="z.B. Netzwerkgrundlagen, Datenbankdesign, Buchhaltung"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Freitext-Fragen -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            Freitext-Fragen *
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
          Keine Fragen vorhanden. Fügen Sie mindestens eine Frage hinzu.
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
            <!-- Fragetext -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Fragestellung *
              </label>
              <textarea
                v-model="question.question_text"
                rows="3"
                placeholder="Formulieren Sie eine offene Frage, die eine ausführliche Antwort erfordert..."
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Erwartete Kernpunkte -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Erwartete Kernpunkte
              </label>
              <textarea
                v-model="question.expected_points"
                rows="2"
                placeholder="Welche Punkte sollte eine gute Antwort enthalten? (für KI-Bewertung)"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>

            <!-- Punktzahl -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Maximale Punktzahl
              </label>
              <input
                v-model.number="question.max_points"
                type="number"
                min="1"
                max="100"
                class="w-24 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>

            <!-- Mindestlänge -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Mindestlänge (Wörter)
              </label>
              <input
                v-model.number="question.min_words"
                type="number"
                min="10"
                max="1000"
                step="10"
                class="w-24 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Bewertungskriterien -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Bewertungskriterien
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.criteria.content_accuracy"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Inhaltliche Korrektheit</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.criteria.completeness"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Vollständigkeit der Antwort</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.criteria.structure"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Struktur und Aufbau</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.criteria.terminology"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Fachsprache/Terminologie</span>
          </label>
        </div>
      </div>

      <!-- Feedback-Optionen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Feedback-Optionen
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.show_detailed_feedback"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Detailliertes Feedback anzeigen</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.show_model_answer"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Musterantwort nach Abgabe zeigen</span>
          </label>
        </div>
      </div>

      <!-- KI-Hinweis -->
      <div class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
        <p class="text-sm text-blue-800 dark:text-blue-200">
          <strong>KI-Bewertung:</strong> Die Antworten werden automatisch von der KI analysiert und bewertet.
          Die KI gibt konstruktives Feedback zu Stärken und Verbesserungsmöglichkeiten.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/store/modules/desktop'
import { BaseLearningMethodForm } from '@/components/content/admin/learning-methods/forms'

const METHOD_CODE = 18

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

interface Question {
  question_text: string
  expected_points: string
  max_points: number
  min_words: number
}

// Methoden-spezifische Daten
const methodData = ref({
  exam_topic: '',
  questions: [] as Question[],
  criteria: {
    content_accuracy: true,
    completeness: true,
    structure: false,
    terminology: false
  },
  show_detailed_feedback: true,
  show_model_answer: false
})

const addQuestion = () => {
  methodData.value.questions.push({
    question_text: '',
    expected_points: '',
    max_points: 10,
    min_words: 50
  })
}

const removeQuestion = (index: number) => {
  methodData.value.questions.splice(index, 1)
}

// Lade existierende Daten im Edit-Mode
onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.exam_topic = existingData.exam_topic || ''
    methodData.value.questions = existingData.questions || []
    methodData.value.criteria = existingData.criteria || {
      content_accuracy: true,
      completeness: true,
      structure: false,
      terminology: false
    }
    methodData.value.show_detailed_feedback = existingData.show_detailed_feedback ?? true
    methodData.value.show_model_answer = existingData.show_model_answer ?? false
  }
})
</script>
