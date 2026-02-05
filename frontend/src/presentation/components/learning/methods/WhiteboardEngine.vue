<!--
  LearningMethod23Form - Verständnisprüfung

  Tiefgehende Verständniskontrolle, die über reines Faktenwissen hinausgeht.
  Prüft Zusammenhänge, Transferfähigkeit und Anwendungskompetenz.

  KI-Nutzung: Hoch - KI bewertet Verständnistiefe und gibt differenziertes Feedback.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form: _form }">
      <!-- Prüfungsthema -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Prüfungsthema *
        </label>
        <input
          v-model="methodData.topic"
          type="text"
          placeholder="z.B. TCP/IP Protokollstack, Datenbankdesign, Geschäftsprozesse"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Lernziele -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Zu prüfende Lernziele
        </label>
        <textarea
          v-model="methodData.learning_objectives"
          rows="3"
          placeholder="Welche Lernziele sollen geprüft werden? (eins pro Zeile)"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Verständnisfragen -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            Verständnisfragen *
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
          Keine Fragen vorhanden. Fügen Sie Verständnisfragen hinzu.
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
            <!-- Fragetyp/Verständnisebene -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Verständnisebene *
              </label>
              <select
                v-model="question.level"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              >
                <option value="recall">Erinnern - Faktenwissen abrufen</option>
                <option value="understand">Verstehen - Zusammenhänge erklären</option>
                <option value="apply">Anwenden - In neuem Kontext nutzen</option>
                <option value="analyze">Analysieren - Strukturen erkennen</option>
                <option value="evaluate">Bewerten - Kritisch beurteilen</option>
                <option value="create">Erschaffen - Neues entwickeln</option>
              </select>
            </div>

            <!-- Fragestellung -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Fragestellung *
              </label>
              <textarea
                v-model="question.question"
                rows="3"
                placeholder="Formulieren Sie eine Frage, die tiefes Verständnis erfordert..."
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                required
              />
            </div>

            <!-- Kontext/Szenario -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Kontext / Szenario (optional)
              </label>
              <textarea
                v-model="question.context"
                rows="2"
                placeholder="Optional: Konkretes Szenario oder Anwendungsfall..."
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>

            <!-- Erwartete Kernaspekte -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Erwartete Kernaspekte
              </label>
              <textarea
                v-model="question.expected_aspects"
                rows="2"
                placeholder="Welche Aspekte sollte eine gute Antwort abdecken?"
                class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>

            <!-- Punktzahl -->
            <div>
              <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
                Punkte
              </label>
              <input
                v-model.number="question.points"
                type="number"
                min="1"
                max="100"
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
              v-model="methodData.criteria.depth"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Verständnistiefe</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.criteria.connections"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Verknüpfung von Konzepten</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.criteria.examples"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Eigene Beispiele</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.criteria.critical_thinking"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Kritisches Denken</span>
          </label>
        </div>
      </div>

      <!-- Optionen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Optionen
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.allow_resources"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Hilfsmittel erlauben (Open-Book)</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.show_feedback_immediately"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Sofortiges Feedback nach jeder Frage</span>
          </label>
        </div>
      </div>

      <!-- KI-Hinweis -->
      <div class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
        <p class="text-sm text-blue-800 dark:text-blue-200">
          <strong>KI-Bewertung:</strong> Die KI analysiert nicht nur Faktenkorrektheit,
          sondern auch Verständnistiefe, Argumentationsqualität und Transferfähigkeit.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/modules/desktop'
import { BaseLearningMethodForm } from '@/presentation/components/learning/editor/forms'

const METHOD_CODE = 23

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

interface Question {
  level: string
  question: string
  context: string
  expected_aspects: string
  points: number
}

// Methoden-spezifische Daten
const methodData = ref({
  topic: '',
  learning_objectives: '',
  questions: [] as Question[],
  criteria: {
    depth: true,
    connections: true,
    examples: false,
    critical_thinking: false
  },
  allow_resources: false,
  show_feedback_immediately: false
})

const addQuestion = () => {
  methodData.value.questions.push({
    level: 'understand',
    question: '',
    context: '',
    expected_aspects: '',
    points: 10
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
    methodData.value.learning_objectives = existingData.learning_objectives || ''
    methodData.value.questions = existingData.questions || []
    methodData.value.criteria = existingData.criteria || {
      depth: true,
      connections: true,
      examples: false,
      critical_thinking: false
    }
    methodData.value.allow_resources = existingData.allow_resources ?? false
    methodData.value.show_feedback_immediately = existingData.show_feedback_immediately ?? false
  }
})
</script>
