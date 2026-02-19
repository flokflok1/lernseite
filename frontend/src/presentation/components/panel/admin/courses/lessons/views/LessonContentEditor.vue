<!--
  LessonContentEditor - Type-specific content editors

  Renders the appropriate editor based on lesson type:
  - Text (Markdown/HTML textarea)
  - Video (URL + description)
  - Quiz (questions with multiple-choice options)
  - Exam (questions with points)
  - Placeholder for unimplemented types
-->

<template>
  <div v-if="lessonType" class="border-t border-[var(--color-border)] pt-6">
    <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
      {{ typeLabel }} - Inhalt
    </h3>

    <!-- TEXT Editor -->
    <div v-if="lessonType === 'text'" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Text-Inhalt (Markdown/HTML)
        </label>
        <textarea
          v-model="content.text"
          @input="$emit('change')"
          rows="12"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] font-mono text-sm"
          placeholder="# Überschrift

**Fetter Text**, *kursiver Text*

- Liste 1
- Liste 2"
        ></textarea>
        <p class="text-xs text-[var(--color-text-tertiary)] mt-1">Unterstützt Markdown-Formatierung</p>
      </div>
    </div>

    <!-- VIDEO Editor -->
    <div v-else-if="lessonType === 'video'" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Video-URL *
        </label>
        <input
          v-model="content.video_url"
          @input="$emit('change')"
          type="url"
          required
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          placeholder="https://www.youtube.com/watch?v=..."
        />
        <p class="text-xs text-[var(--color-text-tertiary)] mt-1">YouTube, Vimeo oder direkter Link</p>
      </div>

      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Video-Beschreibung
        </label>
        <textarea
          v-model="content.video_description"
          @input="$emit('change')"
          rows="4"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          placeholder="Zusätzliche Informationen zum Video..."
        ></textarea>
      </div>
    </div>

    <!-- QUIZ Editor -->
    <div v-else-if="lessonType === 'quiz'" class="space-y-4">
      <div class="flex items-center justify-between mb-3">
        <h4 class="text-sm font-medium text-[var(--color-text-primary)]">
          Fragen ({{ content.questions.length }})
        </h4>
        <button
          @click="$emit('addQuestion')"
          class="px-3 py-1.5 bg-[var(--color-primary)] text-white text-sm rounded-lg hover:bg-[var(--color-primary-hover)]"
        >
          + Frage hinzufügen
        </button>
      </div>

      <div
        v-for="(question, qIdx) in content.questions"
        :key="qIdx"
        class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 space-y-3"
      >
        <div class="flex items-start justify-between gap-2">
          <div class="flex-1">
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              Frage {{ qIdx + 1 }}
            </label>
            <input
              v-model="question.text"
              @input="$emit('change')"
              type="text"
              required
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              placeholder="Fragentext..."
            />
          </div>
          <button
            @click="$emit('removeQuestion', qIdx)"
            class="p-2 text-red-600 hover:bg-red-500/10 rounded"
            title="Frage löschen"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="space-y-2">
          <label class="block text-sm font-medium text-[var(--color-text-primary)]">
            Antwortoptionen
          </label>
          <div v-for="(option, oIdx) in question.options" :key="oIdx" class="flex items-center gap-2">
            <input
              v-model="question.correct_indices"
              :value="oIdx"
              @change="$emit('change')"
              type="checkbox"
              class="w-4 h-4 text-[var(--color-primary)] border-[var(--color-border)] rounded"
            />
            <input
              v-model="option.text"
              @input="$emit('change')"
              type="text"
              required
              class="flex-1 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              :placeholder="`Option ${oIdx + 1}`"
            />
            <button
              v-if="question.options.length > 2"
              @click="$emit('removeOption', qIdx, oIdx)"
              class="p-2 text-red-600 hover:bg-red-500/10 rounded"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <button
            v-if="question.options.length < 5"
            @click="$emit('addOption', qIdx)"
            class="text-sm text-[var(--color-primary)] hover:underline"
          >
            + Option hinzufügen
          </button>
        </div>
      </div>

      <div v-if="content.questions.length === 0" class="text-center py-8 text-[var(--color-text-tertiary)]">
        Noch keine Fragen. Klicken Sie auf "+ Frage hinzufügen"
      </div>
    </div>

    <!-- EXAM Editor -->
    <div v-else-if="lessonType === 'exam'" class="space-y-4">
      <div class="flex items-center justify-between mb-3">
        <h4 class="text-sm font-medium text-[var(--color-text-primary)]">
          Prüfungsfragen ({{ content.exam_questions.length }})
        </h4>
        <button
          @click="$emit('addExamQuestion')"
          class="px-3 py-1.5 bg-[var(--color-primary)] text-white text-sm rounded-lg hover:bg-[var(--color-primary-hover)]"
        >
          + Frage hinzufügen
        </button>
      </div>

      <div
        v-for="(question, idx) in content.exam_questions"
        :key="idx"
        class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 space-y-3"
      >
        <div class="flex items-start justify-between gap-2">
          <div class="flex-1">
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              Frage {{ idx + 1 }}
            </label>
            <textarea
              v-model="question.text"
              @input="$emit('change')"
              rows="2"
              required
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              placeholder="Fragentext..."
            ></textarea>
          </div>
          <button
            @click="$emit('removeExamQuestion', idx)"
            class="p-2 text-red-600 hover:bg-red-500/10 rounded"
            title="Frage löschen"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div>
          <label class="block text-sm text-[var(--color-text-primary)] mb-1">
            Punkte
          </label>
          <input
            v-model.number="question.points"
            @input="$emit('change')"
            type="number"
            min="1"
            class="w-24 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            placeholder="10"
          />
        </div>
      </div>

      <div v-if="content.exam_questions.length === 0" class="text-center py-8 text-[var(--color-text-tertiary)]">
        Noch keine Prüfungsfragen
      </div>
    </div>

    <!-- OTHER Types Placeholder -->
    <div v-else class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <p class="text-sm text-blue-700">
        Content-Editor für "{{ typeLabel }}" wird in einer zukünftigen Phase implementiert.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { LessonFormContent } from '../composables'

interface Props {
  lessonType: string
  content: LessonFormContent
  typeLabel: string
}

defineProps<Props>()

defineEmits<{
  (e: 'change'): void
  (e: 'addQuestion'): void
  (e: 'removeQuestion', idx: number): void
  (e: 'addOption', questionIdx: number): void
  (e: 'removeOption', questionIdx: number, optionIdx: number): void
  (e: 'addExamQuestion'): void
  (e: 'removeExamQuestion', idx: number): void
}>()
</script>
