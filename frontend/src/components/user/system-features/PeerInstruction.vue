<!--
  LearningMethod26Form - Peer Instruction

  Lernende erklaeren sich gegenseitig Konzepte, KI moderiert und gibt Feedback.
  Basiert auf Eric Mazurs Peer Instruction Methode.

  KI-Nutzung: Mittel - KI moderiert, bewertet Erklaerungen, gibt Feedback.
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
          Thema / Konzept *
        </label>
        <input
          v-model="methodData.topic"
          type="text"
          placeholder="z.B. OSI-Modell, Objektorientierung, Projektmanagement"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Konzept-Frage -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Konzept-Frage *
        </label>
        <textarea
          v-model="methodData.concept_question"
          rows="3"
          placeholder="Die zentrale Frage, die die Lernenden beantworten und diskutieren sollen..."
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Antwortoptionen (Multiple Choice) -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Antwortoptionen
        </label>
        <div class="space-y-2">
          <div
            v-for="(option, index) in methodData.answer_options"
            :key="index"
            class="flex gap-2"
          >
            <input
              v-model="option.text"
              type="text"
              :placeholder="`Option ${String.fromCharCode(65 + index)}`"
              class="flex-1 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
            <label class="flex items-center gap-1 px-2">
              <input
                v-model="option.correct"
                type="checkbox"
                class="rounded border-[var(--color-border)] text-[var(--color-primary)]"
              />
              <span class="text-xs text-[var(--color-text-secondary)]">Richtig</span>
            </label>
            <button
              v-if="methodData.answer_options.length > 2"
              @click="removeOption(index)"
              class="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <button
          v-if="methodData.answer_options.length < 6"
          @click="addOption"
          class="mt-2 text-sm text-[var(--color-primary)] hover:underline"
        >
          + Option hinzufuegen
        </button>
      </div>

      <!-- Gruppen-Einstellungen -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Gruppengroesse
          </label>
          <select
            v-model="methodData.group_size"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option :value="2">2 Personen (Partnerarbeit)</option>
            <option :value="3">3 Personen</option>
            <option :value="4">4 Personen</option>
            <option :value="5">5 Personen</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Diskussionszeit (Minuten)
          </label>
          <input
            v-model.number="methodData.discussion_time"
            type="number"
            min="2"
            max="15"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          />
        </div>
      </div>

      <!-- Phasen -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Peer Instruction Phasen
        </label>
        <div class="space-y-2 text-sm">
          <div class="flex items-center gap-2 p-2 bg-[var(--color-background)] rounded">
            <span class="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs">1</span>
            <span>Individuelle Antwort (ohne Diskussion)</span>
          </div>
          <div class="flex items-center gap-2 p-2 bg-[var(--color-background)] rounded">
            <span class="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs">2</span>
            <span>Peer-Diskussion in Kleingruppen</span>
          </div>
          <div class="flex items-center gap-2 p-2 bg-[var(--color-background)] rounded">
            <span class="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs">3</span>
            <span>Erneute Antwort nach Diskussion</span>
          </div>
          <div class="flex items-center gap-2 p-2 bg-[var(--color-background)] rounded">
            <span class="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs">4</span>
            <span>KI-Erklaerung und Feedback</span>
          </div>
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
              v-model="methodData.show_statistics"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Antwort-Statistiken anzeigen</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.anonymous_voting"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Anonyme Abstimmung</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.require_explanation"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Begruendung erforderlich</span>
          </label>
        </div>
      </div>

      <!-- KI-Hinweis -->
      <div class="p-3 bg-pink-50 dark:bg-pink-900/20 rounded-lg border border-pink-200 dark:border-pink-800">
        <p class="text-sm text-pink-800 dark:text-pink-200">
          <strong>Peer Instruction:</strong> Lernende diskutieren in Kleingruppen und erklaeren
          sich gegenseitig Konzepte. Die KI moderiert, analysiert die Diskussionen und gibt
          gezieltes Feedback.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/store/window.store'
import { BaseLearningMethodForm } from '@/components/admin/content-management/learning-methods/forms'

const METHOD_CODE = 26

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const methodData = ref({
  topic: '',
  concept_question: '',
  answer_options: [
    { text: '', correct: false },
    { text: '', correct: false },
    { text: '', correct: false },
    { text: '', correct: false }
  ],
  group_size: 3,
  discussion_time: 5,
  show_statistics: true,
  anonymous_voting: true,
  require_explanation: false
})

const addOption = () => {
  if (methodData.value.answer_options.length < 6) {
    methodData.value.answer_options.push({ text: '', correct: false })
  }
}

const removeOption = (index: number) => {
  if (methodData.value.answer_options.length > 2) {
    methodData.value.answer_options.splice(index, 1)
  }
}

onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.topic = existingData.topic || ''
    methodData.value.concept_question = existingData.concept_question || ''
    methodData.value.answer_options = existingData.answer_options || methodData.value.answer_options
    methodData.value.group_size = existingData.group_size || 3
    methodData.value.discussion_time = existingData.discussion_time || 5
    methodData.value.show_statistics = existingData.show_statistics ?? true
    methodData.value.anonymous_voting = existingData.anonymous_voting ?? true
    methodData.value.require_explanation = existingData.require_explanation ?? false
  }
})
</script>
