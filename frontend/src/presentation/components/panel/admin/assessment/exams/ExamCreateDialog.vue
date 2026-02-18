<!--
  ExamCreateDialog - Dialog for creating a manual exam.
-->

<template>
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click.self="$emit('close')"
  >
    <div class="bg-[var(--color-surface)] rounded-lg p-6 max-w-md w-full mx-4 border border-[var(--color-border)]">
      <h3 class="text-lg font-bold text-[var(--color-text-primary)] mb-4">
        {{ $t('examManager.create.title') }}
      </h3>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
            {{ $t('examManager.create.examTitle') }}
          </label>
          <input
            :value="form.title"
            @input="updateField('title', ($event.target as HTMLInputElement).value)"
            type="text"
            required
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
            :placeholder="$t('examManager.create.titlePlaceholder')"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
            {{ $t('examManager.create.description') }}
          </label>
          <textarea
            :value="form.description"
            @input="updateField('description', ($event.target as HTMLTextAreaElement).value)"
            rows="3"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
            :placeholder="$t('examManager.create.descriptionPlaceholder')"
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
              {{ $t('examManager.create.durationLabel') }}
            </label>
            <input
              :value="form.duration_minutes"
              @input="updateField('duration_minutes', Number(($event.target as HTMLInputElement).value))"
              type="number"
              min="5"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
              {{ $t('examManager.create.passingScoreLabel') }}
            </label>
            <input
              :value="form.passing_score"
              @input="updateField('passing_score', Number(($event.target as HTMLInputElement).value))"
              type="number"
              min="0"
              max="100"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
            />
          </div>
        </div>
      </div>

      <div class="flex gap-2 mt-6">
        <button
          @click="$emit('submit')"
          :disabled="!canSubmit"
          class="flex-1 px-4 py-2 text-white rounded transition-colors"
          style="background-color: var(--color-success, #16a34a);"
          :class="{ 'opacity-50 cursor-not-allowed': !canSubmit }"
        >
          {{ $t('examManager.create.createButton') }}
        </button>
        <button
          @click="$emit('close')"
          class="px-4 py-2 border border-[var(--color-border)] rounded text-[var(--color-text-primary)] transition-colors"
        >
          {{ $t('examManager.create.cancel') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ExamCreateRequest } from '@/application/services/api/panel-admin'

interface Props {
  form: ExamCreateRequest
  canSubmit: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
  submit: []
  'update:field': [field: string, value: string | number]
}>()

function updateField(field: string, value: string | number): void {
  emit('update:field', field, value)
}
</script>
