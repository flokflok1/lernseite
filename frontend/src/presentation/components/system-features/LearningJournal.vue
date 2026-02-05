<!--
  LearningMethod29Form - Lerntagebuch

  Reflexives Lernen mit regelmaessigen Eintraegen und KI-Feedback.
  Foerdert Metakognition und Selbstreflexion.

  KI-Nutzung: Mittel - KI gibt Feedback auf Eintraege und stellt Reflexionsfragen.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form: _form }">
      <!-- Tagebuch-Titel -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Lerntagebuch-Titel *
        </label>
        <input
          v-model="methodData.journal_title"
          type="text"
          placeholder="z.B. Mein IT-Lernweg, Netzwerk-Reflexionen"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Themenbereich -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Themenbereich
        </label>
        <input
          v-model="methodData.topic_area"
          type="text"
          placeholder="z.B. Netzwerktechnik, Programmierung"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
      </div>

      <!-- Reflexionsfragen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Reflexionsfragen (Leitfragen fuer Eintraege)
        </label>
        <div class="space-y-2">
          <div
            v-for="(question, index) in methodData.reflection_prompts"
            :key="index"
            class="flex gap-2"
          >
            <input
              v-model="methodData.reflection_prompts[index]"
              type="text"
              placeholder="z.B. Was habe ich heute gelernt?"
              class="flex-1 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
            <button
              v-if="methodData.reflection_prompts.length > 1"
              @click="removePrompt(index)"
              class="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <button
          v-if="methodData.reflection_prompts.length < 6"
          @click="addPrompt"
          class="mt-2 text-sm text-[var(--color-primary)] hover:underline"
        >
          + Frage hinzufuegen
        </button>
      </div>

      <!-- Eintrags-Frequenz -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Empfohlene Frequenz
          </label>
          <select
            v-model="methodData.entry_frequency"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option value="daily">Taeglich</option>
            <option value="after_lesson">Nach jeder Lektion</option>
            <option value="weekly">Woechentlich</option>
            <option value="milestone">Bei Meilensteinen</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Min. Eintragslaenge
          </label>
          <select
            v-model="methodData.min_entry_length"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option :value="50">50 Woerter</option>
            <option :value="100">100 Woerter</option>
            <option :value="200">200 Woerter</option>
            <option :value="0">Keine Mindestlaenge</option>
          </select>
        </div>
      </div>

      <!-- Eintrag-Kategorien -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Eintrag-Kategorien
        </label>
        <div class="grid grid-cols-2 gap-2">
          <label
            v-for="category in availableCategories"
            :key="category.value"
            class="flex items-center gap-2 cursor-pointer"
          >
            <input
              v-model="methodData.categories"
              type="checkbox"
              :value="category.value"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">{{ category.label }}</span>
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
              v-model="methodData.ai_feedback"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">KI-Feedback auf Eintraege</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.mood_tracking"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Stimmungs-Tracking</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.private_entries"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Eintraege sind privat</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.show_progress"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Lernfortschritt visualisieren</span>
          </label>
        </div>
      </div>

      <!-- KI-Hinweis -->
      <div class="p-3 bg-pink-50 dark:bg-pink-900/20 rounded-lg border border-pink-200 dark:border-pink-800">
        <p class="text-sm text-pink-800 dark:text-pink-200">
          <strong>Lerntagebuch:</strong> Regelmaessige Reflexion ueber das Gelernte foerdert
          tieferes Verstaendnis und Metakognition. Die KI gibt konstruktives Feedback.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/window.store'
import { BaseLearningMethodForm } from '@/presentation/components/learning/editor/forms'

const METHOD_CODE = 29

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const availableCategories = [
  { value: 'learned', label: 'Was ich gelernt habe' },
  { value: 'challenges', label: 'Herausforderungen' },
  { value: 'questions', label: 'Offene Fragen' },
  { value: 'connections', label: 'Verbindungen zu anderem' },
  { value: 'applications', label: 'Anwendungsideen' },
  { value: 'emotions', label: 'Gefuehle/Motivation' }
]

const methodData = ref({
  journal_title: '',
  topic_area: '',
  reflection_prompts: [
    'Was habe ich heute Neues gelernt?',
    'Was war besonders interessant oder ueberraschend?',
    'Wo hatte ich Schwierigkeiten?'
  ],
  entry_frequency: 'after_lesson',
  min_entry_length: 100,
  categories: ['learned', 'challenges'],
  ai_feedback: true,
  mood_tracking: false,
  private_entries: true,
  show_progress: true
})

const addPrompt = () => {
  if (methodData.value.reflection_prompts.length < 6) {
    methodData.value.reflection_prompts.push('')
  }
}

const removePrompt = (index: number) => {
  if (methodData.value.reflection_prompts.length > 1) {
    methodData.value.reflection_prompts.splice(index, 1)
  }
}

onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.journal_title = existingData.journal_title || ''
    methodData.value.topic_area = existingData.topic_area || ''
    methodData.value.reflection_prompts = existingData.reflection_prompts || methodData.value.reflection_prompts
    methodData.value.entry_frequency = existingData.entry_frequency || 'after_lesson'
    methodData.value.min_entry_length = existingData.min_entry_length || 100
    methodData.value.categories = existingData.categories || ['learned', 'challenges']
    methodData.value.ai_feedback = existingData.ai_feedback ?? true
    methodData.value.mood_tracking = existingData.mood_tracking ?? false
    methodData.value.private_entries = existingData.private_entries ?? true
    methodData.value.show_progress = existingData.show_progress ?? true
  }
})
</script>
