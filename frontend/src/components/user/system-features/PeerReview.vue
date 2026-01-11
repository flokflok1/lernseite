<!--
  LearningMethod28Form - Peer Review

  Gegenseitige Bewertung von Arbeiten nach definierten Kriterien.
  Lernende geben und erhalten strukturiertes Feedback.

  KI-Nutzung: Mittel - KI unterstuetzt bei Feedback-Qualitaet und Fairness.
-->

<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <!-- Review-Titel -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Review-Titel *
        </label>
        <input
          v-model="methodData.review_title"
          type="text"
          placeholder="z.B. Code-Review Uebung, Projekt-Dokumentation Feedback"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Aufgabenbeschreibung -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Aufgabe fuer die Einreichung *
        </label>
        <textarea
          v-model="methodData.submission_task"
          rows="3"
          placeholder="Beschreiben Sie, was die Lernenden einreichen sollen..."
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          required
        />
      </div>

      <!-- Bewertungskriterien -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Bewertungskriterien
        </label>
        <div class="space-y-2">
          <div
            v-for="(criterion, index) in methodData.criteria"
            :key="index"
            class="flex gap-2"
          >
            <input
              v-model="criterion.name"
              type="text"
              placeholder="Kriterium (z.B. Vollstaendigkeit)"
              class="flex-1 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
            <select
              v-model="criterion.weight"
              class="w-24 px-2 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)]"
            >
              <option :value="1">1x</option>
              <option :value="2">2x</option>
              <option :value="3">3x</option>
            </select>
            <button
              v-if="methodData.criteria.length > 1"
              @click="removeCriterion(index)"
              class="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <button
          v-if="methodData.criteria.length < 8"
          @click="addCriterion"
          class="mt-2 text-sm text-[var(--color-primary)] hover:underline"
        >
          + Kriterium hinzufuegen
        </button>
      </div>

      <!-- Bewertungsskala -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Bewertungsskala
        </label>
        <select
          v-model="methodData.rating_scale"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        >
          <option value="stars_5">5 Sterne</option>
          <option value="points_10">1-10 Punkte</option>
          <option value="grades">Schulnoten (1-6)</option>
          <option value="thumbs">Daumen hoch/runter</option>
          <option value="rubric">Rubrik (Anfaenger/Fortgeschritten/Experte)</option>
        </select>
      </div>

      <!-- Reviews pro Arbeit -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Reviews pro Einreichung
          </label>
          <select
            v-model="methodData.reviews_per_submission"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option :value="1">1 Review</option>
            <option :value="2">2 Reviews</option>
            <option :value="3">3 Reviews</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Min. Feedback-Laenge
          </label>
          <select
            v-model="methodData.min_feedback_length"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option :value="50">50 Zeichen</option>
            <option :value="100">100 Zeichen</option>
            <option :value="200">200 Zeichen</option>
            <option :value="0">Keine Mindestlaenge</option>
          </select>
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
              v-model="methodData.anonymous_reviews"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Anonyme Reviews</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.self_review"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Selbstbewertung erforderlich</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.ai_quality_check"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">KI prueft Feedback-Qualitaet</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="methodData.allow_revision"
              type="checkbox"
              class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
            />
            <span class="text-sm text-[var(--color-text-primary)]">Ueberarbeitung nach Feedback erlauben</span>
          </label>
        </div>
      </div>

      <!-- KI-Hinweis -->
      <div class="p-3 bg-pink-50 dark:bg-pink-900/20 rounded-lg border border-pink-200 dark:border-pink-800">
        <p class="text-sm text-pink-800 dark:text-pink-200">
          <strong>Peer Review:</strong> Lernende bewerten gegenseitig ihre Arbeiten.
          Das foerdert kritisches Denken und verbessert die eigene Arbeit durch Feedback.
        </p>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/store/window.store'
import { BaseLearningMethodForm } from '@/components/content/admin/learning-methods/forms'

const METHOD_CODE = 28

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const methodData = ref({
  review_title: '',
  submission_task: '',
  criteria: [
    { name: 'Vollstaendigkeit', weight: 2 },
    { name: 'Korrektheit', weight: 2 },
    { name: 'Klarheit', weight: 1 }
  ],
  rating_scale: 'stars_5',
  reviews_per_submission: 2,
  min_feedback_length: 100,
  anonymous_reviews: true,
  self_review: false,
  ai_quality_check: true,
  allow_revision: true
})

const addCriterion = () => {
  if (methodData.value.criteria.length < 8) {
    methodData.value.criteria.push({ name: '', weight: 1 })
  }
}

const removeCriterion = (index: number) => {
  if (methodData.value.criteria.length > 1) {
    methodData.value.criteria.splice(index, 1)
  }
}

onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value.review_title = existingData.review_title || ''
    methodData.value.submission_task = existingData.submission_task || ''
    methodData.value.criteria = existingData.criteria || methodData.value.criteria
    methodData.value.rating_scale = existingData.rating_scale || 'stars_5'
    methodData.value.reviews_per_submission = existingData.reviews_per_submission || 2
    methodData.value.min_feedback_length = existingData.min_feedback_length || 100
    methodData.value.anonymous_reviews = existingData.anonymous_reviews ?? true
    methodData.value.self_review = existingData.self_review ?? false
    methodData.value.ai_quality_check = existingData.ai_quality_check ?? true
    methodData.value.allow_revision = existingData.allow_revision ?? true
  }
})
</script>
