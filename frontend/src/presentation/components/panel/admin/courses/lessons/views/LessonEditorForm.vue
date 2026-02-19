<!--
  LessonEditorForm - Shared lesson editor form layout

  Contains the common form fields and delegates to LessonContentEditor
  for type-specific content. Used by LessonEditorWindow, LessonEditorPanel,
  and LessonEditor to avoid template duplication.
-->

<template>
  <div class="h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header with Context & Save Status -->
    <div class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-4 py-3">
      <div class="flex items-center justify-between">
        <p class="text-xs text-[var(--color-text-secondary)]">
          <slot name="header-label">
            Modul: <span class="font-medium text-[var(--color-text-primary)]">Modul {{ moduleId }}</span>
          </slot>
        </p>
        <!-- Save Status Indicator -->
        <div class="flex items-center gap-2 text-xs">
          <span v-if="saveStatus === 'saving'" class="text-blue-600 flex items-center gap-1">
            <svg class="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ savingLabel }}
          </span>
          <span v-else-if="saveStatus === 'saved'" class="text-green-600 flex items-center gap-1">
            <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            {{ savedLabel }}
          </span>
          <span v-else-if="saveStatus === 'error'" class="text-red-600">
            {{ errorMessage || errorLabel }}
          </span>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-6">
      <div class="space-y-6 max-w-3xl mx-auto">
        <!-- Title -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ titleLabel }}
          </label>
          <input
            v-model="form.title"
            @input="$emit('debouncedSave')"
            type="text"
            required
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            :placeholder="titlePlaceholder"
          />
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ descriptionLabel }}
          </label>
          <textarea
            v-model="form.description"
            @input="$emit('debouncedSave')"
            rows="3"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            :placeholder="descriptionPlaceholder"
          ></textarea>
        </div>

        <!-- Lesson Type -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ typeSelectLabel }}
          </label>
          <select
            v-model="form.lesson_type"
            @change="$emit('typeChange')"
            required
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option value="">{{ typeDefaultOption }}</option>
            <option v-for="option in typeOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>

        <!-- Order & Duration -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              {{ orderLabel }}
            </label>
            <input
              v-model.number="form.order_index"
              @input="$emit('debouncedSave')"
              type="number"
              min="1"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              :placeholder="orderPlaceholder"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              {{ durationLabel }}
            </label>
            <input
              v-model.number="form.duration_minutes"
              @input="$emit('debouncedSave')"
              type="number"
              min="0"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              :placeholder="durationPlaceholder"
            />
          </div>
        </div>

        <!-- Type-Specific Content -->
        <LessonContentEditor
          :lesson-type="form.lesson_type"
          :content="form.content"
          :type-label="lessonTypeLabel"
          @change="$emit('debouncedSave')"
          @add-question="$emit('addQuestion')"
          @remove-question="(idx: number) => $emit('removeQuestion', idx)"
          @add-option="(qIdx: number) => $emit('addOption', qIdx)"
          @remove-option="(qIdx: number, oIdx: number) => $emit('removeOption', qIdx, oIdx)"
          @add-exam-question="$emit('addExamQuestion')"
          @remove-exam-question="(idx: number) => $emit('removeExamQuestion', idx)"
        />

        <!-- Validation Messages -->
        <div v-if="validationErrors.length > 0" class="bg-red-50 border border-red-200 rounded-lg p-4">
          <p class="text-sm font-semibold text-red-800 mb-2">{{ validationTitle }}</p>
          <ul class="list-disc list-inside text-sm text-red-700 space-y-1">
            <li v-for="(error, idx) in validationErrors" :key="idx">{{ error }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import LessonContentEditor from './LessonContentEditor.vue'
import type { LessonForm, SaveStatus } from '../composables'

interface LessonTypeOption {
  value: string
  label: string
}

interface Props {
  form: LessonForm
  saveStatus: SaveStatus
  errorMessage: string | null
  moduleId: number | undefined
  lessonTypeLabel: string
  validationErrors: string[]
  titleLabel?: string
  titlePlaceholder?: string
  descriptionLabel?: string
  descriptionPlaceholder?: string
  typeSelectLabel?: string
  typeDefaultOption?: string
  typeOptions?: LessonTypeOption[]
  orderLabel?: string
  orderPlaceholder?: string
  durationLabel?: string
  durationPlaceholder?: string
  savingLabel?: string
  savedLabel?: string
  errorLabel?: string
  validationTitle?: string
}

withDefaults(defineProps<Props>(), {
  titleLabel: 'Lektionstitel *',
  titlePlaceholder: 'z.B. Variablen und Datentypen',
  descriptionLabel: 'Beschreibung',
  descriptionPlaceholder: 'Kurze Beschreibung der Lektion...',
  typeSelectLabel: 'Lektionstyp *',
  typeDefaultOption: 'Bitte w\u00E4hlen...',
  typeOptions: () => [
    { value: 'text', label: '\uD83D\uDCC4 Text' },
    { value: 'video', label: '\uD83C\uDFA5 Video' },
    { value: 'quiz', label: '\u2753 Quiz' },
    { value: 'interactive', label: '\uD83C\uDFAE Interaktiv' },
    { value: 'exercise', label: '\uD83D\uDCAA \u00DCbung' },
    { value: 'ai', label: '\uD83E\uDD16 KI-Lektion' },
    { value: 'exam', label: '\uD83D\uDCDD Pr\u00FCfung' }
  ],
  orderLabel: 'Reihenfolge',
  orderPlaceholder: '1',
  durationLabel: 'Dauer (Minuten)',
  durationPlaceholder: '15',
  savingLabel: 'Speichern...',
  savedLabel: 'Gespeichert',
  errorLabel: 'Fehler',
  validationTitle: 'Bitte beheben Sie folgende Fehler:'
})

defineEmits<{
  (e: 'debouncedSave'): void
  (e: 'typeChange'): void
  (e: 'addQuestion'): void
  (e: 'removeQuestion', idx: number): void
  (e: 'addOption', questionIdx: number): void
  (e: 'removeOption', questionIdx: number, optionIdx: number): void
  (e: 'addExamQuestion'): void
  (e: 'removeExamQuestion', idx: number): void
}>()
</script>
