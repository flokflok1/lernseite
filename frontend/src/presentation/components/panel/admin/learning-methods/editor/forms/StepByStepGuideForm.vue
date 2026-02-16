<!--
  LearningMethod04Form - Sokratischer Dialog

  KI fuehrt durch gezielte Fragen zum Verstaendnis (Sokratische Methode).
  Der Lernende wird durch Fragen dazu gebracht, selbst auf die Loesung zu kommen.

  KI-Nutzung: Sehr Hoch - KI fuehrt adaptiven Dialog mit Verstaendnisfragen.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form: _form }">
      <!-- Themenbereich -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Thema / Konzept *
        </label>
        <input
          v-model="methodData.topic"
          type="text"
          placeholder="z.B. Subnetting, Rekursion, SOLID-Prinzipien"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Lernziel -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Lernziel
        </label>
        <textarea
          v-model="methodData.learning_goal"
          rows="2"
          placeholder="Was soll der Lernende am Ende verstanden haben?"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Vorwissen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Vorausgesetztes Vorwissen
        </label>
        <select
          v-model="methodData.prior_knowledge"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="none">Kein Vorwissen noetig</option>
          <option value="basic">Grundlagen bekannt</option>
          <option value="intermediate">Fortgeschrittenes Wissen</option>
          <option value="advanced">Expertenwissen</option>
        </select>
      </div>

      <!-- Dialog-Stil -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Dialog-Stil
        </label>
        <div class="grid grid-cols-2 gap-3">
          <label
            v-for="style in dialogStyles"
            :key="style.value"
            class="flex items-start p-3 border rounded-lg cursor-pointer transition-all"
            :class="methodData.dialog_style === style.value
              ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/10'
              : 'border-[var(--color-border)] hover:border-[var(--color-primary)]/50'"
          >
            <input
              v-model="methodData.dialog_style"
              type="radio"
              :value="style.value"
              class="sr-only"
            />
            <div>
              <span class="text-lg mr-2">{{ style.icon }}</span>
              <span class="font-medium text-[var(--color-text-primary)]">{{ style.label }}</span>
              <p class="text-xs text-[var(--color-text-secondary)] mt-1">{{ style.description }}</p>
            </div>
          </label>
        </div>
      </div>

      <!-- Fragen-Tiefe -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Fragen-Tiefe
        </label>
        <div class="flex items-center gap-4">
          <input
            v-model.number="methodData.question_depth"
            type="range"
            min="1"
            max="5"
            step="1"
            class="flex-1"
          />
          <span class="text-sm font-medium text-[var(--color-text-primary)] w-24 text-center">
            {{ depthLabels[methodData.question_depth - 1] }}
          </span>
        </div>
        <p class="mt-1 text-xs text-[var(--color-text-secondary)]">
          Wie tief soll die KI nachfragen? (1 = Oberflaeche, 5 = Tiefgruendig)
        </p>
      </div>

      <!-- Max Fragen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Maximale Frageanzahl
        </label>
        <div class="flex items-center gap-4">
          <input
            v-model.number="methodData.max_questions"
            type="range"
            min="3"
            max="15"
            step="1"
            class="flex-1"
          />
          <span class="text-sm font-medium text-[var(--color-text-primary)] w-12 text-center">
            {{ methodData.max_questions }}
          </span>
        </div>
      </div>

      <!-- Optionen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Dialog-Optionen
        </label>
        <div class="space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.allow_hints"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Hinweise auf Anfrage geben</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.provide_summary"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Zusammenfassung am Ende</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.adaptive_difficulty"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Schwierigkeit adaptiv anpassen</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.show_progress"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Fortschritt anzeigen</span>
          </label>
        </div>
      </div>

      <!-- Start-Frage (optional) -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Start-Frage (optional)
        </label>
        <textarea
          v-model="methodData.initial_question"
          rows="2"
          placeholder="Optional: Eigene Einstiegsfrage definieren..."
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- KI-Hinweis -->
      <div class="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
        <p class="text-sm text-purple-800 dark:text-purple-200">
          <strong>Sokratische Methode:</strong> Die KI stellt gezielte Fragen, um den Lernenden
          zum selbstaendigen Denken anzuregen. Statt Antworten zu geben, fuehrt sie durch
          Fragen zur Erkenntnis.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 4

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const dialogStyles = [
  {
    value: 'classic',
    icon: '🏛️',
    label: 'Klassisch',
    description: 'Traditionelle sokratische Fragen'
  },
  {
    value: 'guided',
    icon: '🧭',
    label: 'Gefuehrt',
    description: 'Mehr Struktur und Hinweise'
  },
  {
    value: 'challenging',
    icon: '🎯',
    label: 'Herausfordernd',
    description: 'Anspruchsvolle Rueckfragen'
  },
  {
    value: 'exploratory',
    icon: '🔍',
    label: 'Explorativ',
    description: 'Offene Erkundung des Themas'
  }
]

const depthLabels = ['Oberflaeche', 'Einstieg', 'Mittel', 'Vertiefung', 'Tiefgruendig']

// Methoden-spezifische Daten
const methodData = ref({
  topic: '',
  learning_goal: '',
  prior_knowledge: 'basic',
  dialog_style: 'classic',
  question_depth: 3,
  max_questions: 8,
  allow_hints: true,
  provide_summary: true,
  adaptive_difficulty: true,
  show_progress: true,
  initial_question: ''
})

// Lade existierende Daten im Edit-Mode
onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.topic = existingData.topic || ''
    methodData.value.learning_goal = existingData.learning_goal || ''
    methodData.value.prior_knowledge = existingData.prior_knowledge || 'basic'
    methodData.value.dialog_style = existingData.dialog_style || 'classic'
    methodData.value.question_depth = existingData.question_depth || 3
    methodData.value.max_questions = existingData.max_questions || 8
    methodData.value.allow_hints = existingData.allow_hints ?? true
    methodData.value.provide_summary = existingData.provide_summary ?? true
    methodData.value.adaptive_difficulty = existingData.adaptive_difficulty ?? true
    methodData.value.show_progress = existingData.show_progress ?? true
    methodData.value.initial_question = existingData.initial_question || ''
  }
})
</script>
