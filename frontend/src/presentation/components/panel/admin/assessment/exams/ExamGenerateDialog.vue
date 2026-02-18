<!--
  ExamGenerateDialog - Dialog for AI-powered exam generation.
-->

<template>
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click.self="$emit('close')"
  >
    <div class="bg-[var(--color-surface)] rounded-lg p-6 max-w-2xl w-full mx-4 border border-[var(--color-border)] max-h-[90vh] overflow-y-auto">
      <h3 class="text-lg font-bold text-[var(--color-text-primary)] mb-4 flex items-center gap-2">
        <span>{{ $t('examManager.generate.title') }}</span>
      </h3>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
            {{ $t('examManager.generate.examTitle') }}
          </label>
          <input
            v-model="localForm.title"
            type="text"
            required
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
            :placeholder="$t('examManager.generate.titlePlaceholder')"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
            {{ $t('examManager.generate.examStandard') }}
          </label>
          <select
            v-model="localForm.exam_standard"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
          >
            <option value="IHK_FISI_AP1">IHK FISI AP1</option>
            <option value="IHK_FIAE_AP1">IHK FIAE AP1</option>
            <option value="CompTIA_A+">CompTIA A+</option>
            <option value="CompTIA_Network+">CompTIA Network+</option>
            <option value="Abitur_Informatik">Abitur Informatik</option>
            <option value="Custom">Custom</option>
          </select>
        </div>

        <div class="grid grid-cols-3 gap-3">
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
              {{ $t('examManager.generate.difficulty') }}
            </label>
            <select
              v-model="localForm.difficulty"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
            >
              <option value="beginner">{{ $t('examManager.generate.difficultyBeginner') }}</option>
              <option value="intermediate">{{ $t('examManager.generate.difficultyIntermediate') }}</option>
              <option value="advanced">{{ $t('examManager.generate.difficultyAdvanced') }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
              {{ $t('examManager.generate.durationLabel') }}
            </label>
            <input
              v-model.number="localForm.duration_minutes"
              type="number"
              min="30"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
              {{ $t('examManager.generate.passingScoreLabel') }}
            </label>
            <input
              v-model.number="localForm.passing_score"
              type="number"
              min="0"
              max="100"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ $t('examManager.generate.questionDistribution') }}
          </label>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-[var(--color-text-secondary)]">
                {{ $t('examManager.generate.mcq') }}
              </label>
              <input
                v-model.number="localForm.question_distribution.mcq"
                type="number"
                min="0"
                class="w-full px-2 py-1 text-sm border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
              />
            </div>
            <div>
              <label class="text-xs text-[var(--color-text-secondary)]">
                {{ $t('examManager.generate.fillBlanks') }}
              </label>
              <input
                v-model.number="localForm.question_distribution.fill_blanks"
                type="number"
                min="0"
                class="w-full px-2 py-1 text-sm border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
              />
            </div>
            <div>
              <label class="text-xs text-[var(--color-text-secondary)]">
                {{ $t('examManager.generate.shortAnswer') }}
              </label>
              <input
                v-model.number="localForm.question_distribution.short_answer"
                type="number"
                min="0"
                class="w-full px-2 py-1 text-sm border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
              />
            </div>
            <div>
              <label class="text-xs text-[var(--color-text-secondary)]">
                {{ $t('examManager.generate.caseStudy') }}
              </label>
              <input
                v-model.number="localForm.question_distribution.case_study"
                type="number"
                min="0"
                class="w-full px-2 py-1 text-sm border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
              />
            </div>
          </div>
          <p class="text-xs text-[var(--color-text-secondary)] mt-1">
            {{ $t('examManager.generate.totalQuestions', { count: totalQuestions }) }}
          </p>
        </div>
      </div>

      <div class="flex gap-2 mt-6">
        <button
          @click="$emit('submit')"
          :disabled="!canSubmit"
          class="flex-1 px-4 py-2 text-white rounded transition-colors flex items-center justify-center gap-2"
          style="background-color: var(--color-primary, #7c3aed);"
          :class="{ 'opacity-50 cursor-not-allowed': !canSubmit }"
        >
          <span>{{ $t('examManager.generate.startGeneration') }}</span>
        </button>
        <button
          @click="$emit('close')"
          class="px-4 py-2 border border-[var(--color-border)] rounded text-[var(--color-text-primary)] transition-colors"
        >
          {{ $t('examManager.generate.cancel') }}
        </button>
      </div>

      <div
        class="mt-4 rounded-lg p-3 border text-xs"
        style="background-color: var(--color-info-bg, #eff6ff); border-color: var(--color-info-border, #bfdbfe);"
      >
        <p style="color: var(--color-info-text, #1e40af);">
          <strong>{{ $t('common.note') }}:</strong> {{ $t('examManager.generate.hint') }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ExamGenerateRequest } from '@/application/services/api/panel-admin'

interface Props {
  localForm: ExamGenerateRequest
  totalQuestions: number
  canSubmit: boolean
}

defineProps<Props>()

defineEmits<{
  close: []
  submit: []
}>()
</script>
