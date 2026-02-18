<!--
  MethodEditModal - Modal for editing an existing learning method instance.
  Provides fields for title, instructions, duration, difficulty, and tier.
-->

<template>
  <div
    v-if="editingMethod"
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    @click.self="$emit('close')"
  >
    <div class="bg-[var(--color-surface)] rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
      <div class="p-4 border-b border-[var(--color-border)] flex items-center justify-between">
        <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
          {{ $t('learningMethodEditor.editMethod') }}
        </h3>
        <button
          @click="$emit('close')"
          class="p-1 rounded hover:bg-[var(--color-background)]"
        >
          <svg class="w-5 h-5 text-[var(--color-text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="p-4 overflow-y-auto max-h-[60vh] space-y-4">
        <!-- Method Type (readonly) -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ $t('learningMethodEditor.methodType') }}
          </label>
          <div class="flex items-center gap-2">
            <span
              class="text-sm font-mono px-2 py-1 rounded"
              :style="getGroupStyle(getMethodGroup(editingMethod.method_type))"
            >
              {{ getGroupPositionById(editingMethod.method_type) }}
            </span>
            <span class="text-[var(--color-text-primary)]">
              {{ getMethodTypeName(editingMethod.method_type) }}
            </span>
          </div>
        </div>

        <!-- Title -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ $t('learningMethodEditor.methodTitle') }}
          </label>
          <input
            :value="editForm.title"
            @input="$emit('update:editForm', { ...editForm, title: ($event.target as HTMLInputElement).value })"
            type="text"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            :placeholder="$t('learningMethodEditor.titlePlaceholder')"
          />
        </div>

        <!-- Instructions -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ $t('learningMethodEditor.instructions') }}
          </label>
          <textarea
            :value="editForm.instructions"
            @input="$emit('update:editForm', { ...editForm, instructions: ($event.target as HTMLTextAreaElement).value })"
            rows="3"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            :placeholder="$t('learningMethodEditor.instructionsPlaceholder')"
          ></textarea>
        </div>

        <!-- Duration & Difficulty -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              {{ $t('learningMethodEditor.duration') }}
            </label>
            <input
              :value="editForm.duration_minutes"
              @input="$emit('update:editForm', { ...editForm, duration_minutes: Number(($event.target as HTMLInputElement).value) })"
              type="number"
              min="1"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              {{ $t('learningMethodEditor.difficulty') }}
            </label>
            <select
              :value="editForm.difficulty"
              @change="$emit('update:editForm', { ...editForm, difficulty: ($event.target as HTMLSelectElement).value })"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            >
              <option value="easy">{{ $t('learningMethodEditor.difficultyOptions.easy') }}</option>
              <option value="medium">{{ $t('learningMethodEditor.difficultyOptions.medium') }}</option>
              <option value="hard">{{ $t('learningMethodEditor.difficultyOptions.hard') }}</option>
            </select>
          </div>
        </div>

        <!-- Tier -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ $t('learningMethodEditor.tier') }}
          </label>
          <select
            :value="editForm.tier"
            @change="$emit('update:editForm', { ...editForm, tier: ($event.target as HTMLSelectElement).value })"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option value="basic">{{ $t('learningMethodEditor.tierOptions.basic') }}</option>
            <option value="premium">{{ $t('learningMethodEditor.tierOptions.premium') }}</option>
            <option value="pro">{{ $t('learningMethodEditor.tierOptions.pro') }}</option>
          </select>
        </div>
      </div>

      <div class="p-4 border-t border-[var(--color-border)] flex justify-end gap-3">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-sm border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-background)] transition-colors"
        >
          {{ $t('learningMethodEditor.cancel') }}
        </button>
        <button
          @click="$emit('save')"
          class="px-4 py-2 text-sm bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors"
        >
          {{ $t('learningMethodEditor.save') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AdminLearningMethod, LearningMethodGroup } from '@/application/services/api/panel-admin'
import type { EditFormData } from './composables/useLearningMethodEditor'

interface Props {
  editingMethod: AdminLearningMethod | null
  editForm: EditFormData
  getGroupStyle: (group: LearningMethodGroup) => string
  getMethodGroup: (methodType: number) => LearningMethodGroup
  getGroupPositionById: (methodTypeId: number) => string
  getMethodTypeName: (methodType: number) => string
}

defineProps<Props>()

defineEmits<{
  close: []
  save: []
  'update:editForm': [form: EditFormData]
}>()
</script>
